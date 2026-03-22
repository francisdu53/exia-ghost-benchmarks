"""
HaluMem Benchmark — EXIA GHOST Adapter

Runs the HaluMem evaluation protocol against EXIA GHOST V5 memory system.

Three operations per session:
  1. Memory Extraction: inject dialogue → extract stored memories
  2. Memory Update: search for updated memories (is_update=True)
  3. Question Answering: retrieve context + LLM answer

Usage:
  python eval_exiaghost.py --users 1        # 1 user (validation)
  python eval_exiaghost.py --users 20       # full benchmark
  python eval_exiaghost.py --users 1 --dry  # dry run (no LLM calls)
"""

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Ensure project root on PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from exia.core.types import EpisodicEntry, SemanticEntry
from exia.memories.episodic import EpisodicMemory
from exia.memories.semantic import SemanticMemory
from exia.providers.embedder import Embedder

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
logger = logging.getLogger("halumem")
logger.setLevel(logging.INFO)

# ═══════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════

DATASET_PATH = Path(__file__).parent / "data" / "HaluMem-Medium.jsonl"
RESULTS_DIR = Path(__file__).parent / "results" / "exiaghost-v5"
FRAME_NAME = "exiaghost"
VERSION = "v5-cp3"

# ═══════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════

def _make_semantic_entry(text: str, vector: np.ndarray, user_id: str,
                         timestamp: str, source_type: str = "conversation") -> SemanticEntry:
    return SemanticEntry(
        id=f"sem_{uuid.uuid4().hex[:12]}",
        concept=text[:100],
        definition=text,
        vector=vector,
        source=user_id,
        source_type=source_type,
        trust_level=0.8,
        learned_at=_parse_timestamp(timestamp),
        usage_count=1,
        confidence=0.5,
        emotional_context=0.0,
        tags=[],
        user_id=user_id,
        privacy="normal",
    )


def _make_episodic_entry(text: str, vector: np.ndarray, user_id: str,
                         timestamp: str) -> EpisodicEntry:
    return EpisodicEntry(
        id=f"ep_{uuid.uuid4().hex[:12]}",
        content=text,
        context="halumem_benchmark",
        vector=vector,
        timestamp=_parse_timestamp(timestamp),
        emotional_intensity=0.3,
        novelty=0.5,
        participants=["user"],
        user_id=user_id,
        privacy="normal",
        consolidated=False,
        faded=False,
    )


def _parse_timestamp(ts: str) -> datetime:
    """Parse HaluMem timestamp format."""
    for fmt in ("%b %d, %Y, %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.now()


def _extract_user_name(persona_info: str) -> str:
    """Extract user name from persona_info string."""
    if "Name:" in persona_info:
        part = persona_info.split("Name:")[1]
        name = part.split(";")[0].strip()
        return name
    return "unknown"


# ═══════════════════════════════════════════════════════
# Core adapter
# ═══════════════════════════════════════════════════════

class ExiaGhostAdapter:
    """Adapter between HaluMem benchmark and EXIA GHOST memory system."""

    def __init__(self, chromadb_path: str, embedder: Embedder,
                 llm_fn=None, dry_run: bool = False):
        self.embedder = embedder
        self.semantic = SemanticMemory(chromadb_path, collection_name="halumem_sem")
        self.episodic = EpisodicMemory(chromadb_path, collection_name="halumem_epi")
        self.llm_fn = llm_fn
        self.dry_run = dry_run
        self._seen_ids: set = set()  # Track already-returned memory IDs

        # Inject NLI ensemble for consolidation (CP3-T9)
        try:
            from sentence_transformers import CrossEncoder
            nli_base = CrossEncoder("cross-encoder/nli-deberta-v3-base")
            nli_small = CrossEncoder("cross-encoder/nli-deberta-v3-small")
            self.semantic.set_nli_model(nli_base, model_alt=nli_small)
            self.episodic.set_nli_model(nli_base, model_alt=nli_small)
            logger.info("NLI ensemble loaded for consolidation")
        except Exception as e:
            logger.warning("NLI not available: %s", e)

    def embed(self, text: str) -> np.ndarray:
        return self.embedder.embed(text)

    @staticmethod
    def _split_into_facts(text: str) -> List[str]:
        """Split message into atomic factual sentences (same as orchestrator)."""
        _NOISE = ("hello", "hi ", "hey", "bonjour", "bonsoir", "salut",
                  "thank", "merci", "thanks", "sure", "of course", "ok",
                  "yes", "no", "oui", "non", "great", "good", "bien",
                  "bye", "goodbye", "au revoir", "d'accord", "alright")

        if not text or len(text) < 15:
            return [text] if text and len(text.strip()) >= 10 else []

        parts = []
        for sep in (".", "!", "?", ";"):
            if sep in text:
                parts = [f.strip() for f in text.split(sep) if f.strip()]
                break
        if not parts:
            parts = [text.strip()]

        filtered = []
        for part in parts:
            if len(part) < 10:
                continue
            if part.lower().startswith(_NOISE):
                continue
            filtered.append(part)

        return filtered if filtered else [text.strip()]

    _EXTRACTION_PROMPT = (
        "You are a memory extraction system. Extract factual memories from the "
        "user's messages in this dialogue.\n\n"
        "# FORMAT RULES (CRITICAL — follow exactly):\n"
        "- ALWAYS use third person: \"{user_name}\" (never \"I\", \"my\", \"me\")\n"
        "- One memory per line\n"
        "- Average length: 15-20 words per memory\n"
        "- No numbering, no bullets, no prefixes\n\n"
        "# MEMORY TYPES TO EXTRACT:\n"
        "1. PERSONA: \"[Name]'s [attribute] is [value]\"\n"
        "   Example: \"{user_name}'s birth date is 1996-08-02\"\n"
        "   Example: \"{user_name} lives in Columbus\"\n\n"
        "2. EVENT: \"[Name] is/has/did [action or situation]\"\n"
        "   Example: \"{user_name} is considering a career change due to mental health impacts\"\n\n"
        "3. RELATIONSHIP: \"[Name]'s [relation] [person], [description]\"\n"
        "   Example: \"{user_name}'s friend Susan provided support during his job transition\"\n\n"
        "# EXTRACTION RULES:\n"
        "- Extract ONLY from user messages (ignore assistant responses)\n"
        "- Include specific dates, names, locations when mentioned\n"
        "- One fact per line — split compound sentences\n"
        "- If user says \"I live in Columbus\" → write \"{user_name} lives in Columbus\"\n"
        "- If user says \"My father is a doctor\" → write \"{user_name}'s father is a doctor\"\n"
        "- Do NOT invent or infer — extract only what is explicitly stated\n"
        "- If no factual memories found, write \"NONE\"\n\n"
        "Dialogue:\n{dialogue}\n\n"
        "Extracted memories:"
    )

    async def add_dialogue(self, dialogue: List[dict], user_id: str,
                           user_name: str = "") -> List[str]:
        """Op 1: Inject dialogue into memory stores + LLM extraction."""
        t0 = time.perf_counter()

        for turn in dialogue:
            text = turn.get("content", "")
            ts = turn.get("timestamp", "")
            if not text:
                continue

            # Store user messages as semantic concepts (split into facts)
            if turn.get("role") == "user":
                sentences = self._split_into_facts(text)
                for sentence in sentences:
                    vector = self.embed(sentence)
                    entry = _make_semantic_entry(sentence, vector, user_id, ts)
                    await self.semantic.store(entry, user_id=user_id)

            # Store all turns as episodes (full text, not split)
            vector = self.embed(text)
            entry = _make_episodic_entry(text, vector, user_id, ts)
            await self.episodic.store(entry, user_id=user_id)

        # LLM extraction — atomic facts in 3rd person
        extracted = []
        if self.llm_fn and not self.dry_run:
            dialogue_text = "\n".join(
                f"[{t.get('timestamp', '')}] {t['role']}: {t['content']}"
                for t in dialogue if t.get("content")
            )
            prompt = self._EXTRACTION_PROMPT.format(
                user_name=user_name or user_id,
                dialogue=dialogue_text,
            )
            try:
                raw = await self.llm_fn(prompt)
                # Parse: one fact per line, filter empty/NONE
                for line in raw.strip().split("\n"):
                    line = line.strip().lstrip("- ").lstrip("• ").strip()
                    if line and line.upper() != "NONE" and len(line) > 10:
                        extracted.append(line)
            except Exception as e:
                logger.warning("LLM extraction failed (non-fatal): %s", e)

        # Fallback if no LLM or extraction failed: use stored memories
        if not extracted:
            extracted = self._get_new_semantic_memories(user_id)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        return extracted, elapsed_ms

    def _get_new_semantic_memories(self, user_id: str) -> List[str]:
        """Get only NEW semantic entries since last call (not cumulative)."""
        try:
            results = self.semantic._collection.get(
                where={"user_id": user_id},
                include=["metadatas"],
            )
            if not results or not results["ids"]:
                return []
            new_memories = []
            for entry_id, meta in zip(results["ids"], results["metadatas"]):
                if entry_id not in self._seen_ids:
                    self._seen_ids.add(entry_id)
                    definition = meta.get("definition", "")
                    if definition:
                        new_memories.append(definition)
            return new_memories
        except Exception as e:
            logger.warning("Failed to get semantic memories: %s", e)
            return []

    async def search_memory(self, query: str, user_id: str,
                            top_k: int = 10) -> tuple:
        """Op 2: Search memories for a query. Returns (formatted_context, results_list, duration_ms)."""
        t0 = time.perf_counter()
        vector = self.embed(query)

        sem_results = await self.semantic.retrieve(
            vector, mode="explore", top_k=top_k, user_id=user_id)
        epi_results = await self.episodic.retrieve(
            vector, mode="NOMINAL", top_k=top_k, user_id=user_id)

        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Format results as timestamped strings
        memory_strings = []
        seen_texts = set()
        for r in sem_results:
            text = r.data.get("definition", "")
            ts = r.data.get("learned_at", "") if "learned_at" in r.data else ""
            if text and text not in seen_texts:
                seen_texts.add(text)
                memory_strings.append((ts, text))
        for r in epi_results:
            text = r.data.get("content", "")
            ts = r.data.get("timestamp", "")
            if text and text not in seen_texts:
                seen_texts.add(text)
                memory_strings.append((ts, text))

        # Format context for LLM with timestamps
        context_lines = []
        for ts, text in memory_strings[:top_k]:
            if ts:
                context_lines.append(f"- [{ts}] {text}")
            else:
                context_lines.append(f"- {text}")
        context = "\n".join(context_lines)

        return context, memory_strings, elapsed_ms

    async def answer_question(self, question: str, context: str) -> tuple:
        """Op 3: Answer a question using retrieved context. Returns (response, duration_ms)."""
        if self.dry_run or self.llm_fn is None:
            return "[DRY RUN — no LLM call]", 0.0

        prompt = (
            "You are a knowledgeable AI assistant with access to personal memories.\n\n"
            "# INSTRUCTIONS:\n"
            "1. Carefully analyze ALL provided memories. Synthesize information "
            "across multiple entries to form a complete answer.\n"
            "2. If memories contain contradictory information, the MOST RECENT "
            "memory (by timestamp) is the source of truth.\n"
            "3. If the question involves relative time references ('last year', "
            "'two months ago'), calculate the actual date from the memory timestamp.\n"
            "4. Your answer must be grounded in the memories. You may use general "
            "knowledge to interpret information found in memories.\n"
            "5. Only say 'Unknown' if the memories contain absolutely NO information "
            "related to the question. If partial information exists, answer with what you have.\n"
            "6. CRITICAL: Your final answer MUST be under 5-6 words. "
            "No explanations, no justifications. Just the answer.\n\n"
            f"Memories:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        t0 = time.perf_counter()
        response = await self.llm_fn(prompt)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        return response, elapsed_ms

    async def run_consolidation(self):
        """Run daily consolidation on both stores."""
        sem_report = await self.semantic.consolidate("daily")
        epi_report = await self.episodic.consolidate("daily")
        logger.info(
            "Consolidation: sem(merged=%d, superseded=%d, pruned=%d) "
            "epi(superseded=%d, pruned=%d)",
            sem_report.entries_merged, sem_report.entries_superseded,
            sem_report.entries_pruned,
            epi_report.entries_superseded, epi_report.entries_pruned,
        )
        return sem_report, epi_report


# ═══════════════════════════════════════════════════════
# LLM provider (Haiku)
# ═══════════════════════════════════════════════════════

async def create_haiku_fn():
    """Create async LLM function using Anthropic Haiku."""
    try:
        from anthropic import AsyncAnthropic
        api_key = os.environ.get("EXIA_ANTHROPIC_API_KEY", "")
        if not api_key:
            # Try loading from .env (check multiple paths)
            for env_dir in [PROJECT_ROOT, PROJECT_ROOT / "..", Path.cwd()]:
                env_path = env_dir / ".env"
                if env_path.exists():
                    for line in env_path.read_text().splitlines():
                        if line.startswith("EXIA_ANTHROPIC_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break
                if api_key:
                    break

        if not api_key:
            logger.warning("No Anthropic API key found — QA will use dry run")
            return None

        client = AsyncAnthropic(api_key=api_key)
        model = "claude-haiku-4-5-20251001"

        async def generate(prompt: str) -> str:
            response = await client.messages.create(
                model=model,
                max_tokens=512,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        logger.info("Haiku LLM ready: %s", model)
        return generate

    except ImportError:
        logger.warning("anthropic package not installed — QA will use dry run")
        return None


# ═══════════════════════════════════════════════════════
# Main benchmark runner
# ═══════════════════════════════════════════════════════

async def process_user(adapter: ExiaGhostAdapter, user_data: dict,
                       run_consolidation_every: int = 10) -> dict:
    """Process a single HaluMem user through EXIA GHOST."""
    user_name = _extract_user_name(user_data.get("persona_info", ""))
    user_id = user_name.lower().replace(" ", "_")
    sessions = user_data["sessions"]

    logger.info("Processing user: %s (%d sessions)", user_name, len(sessions))

    output_sessions = []
    total_extraction_ms = 0
    total_search_ms = 0
    total_response_ms = 0

    for idx, session in enumerate(sessions):
        dialogue = session.get("dialogue", [])
        memory_points = session.get("memory_points", [])
        questions = session.get("questions", [])

        # ── Op 1: Memory Extraction ──
        extracted, add_ms = await adapter.add_dialogue(dialogue, user_id, user_name=user_name)
        total_extraction_ms += add_ms

        # ── Consolidation periodically ──
        if (idx + 1) % run_consolidation_every == 0:
            await adapter.run_consolidation()

        # ── Op 2: Memory Update Check ──
        for mp in memory_points:
            if str(mp.get("is_update", "")).lower() == "true" and mp.get("original_memories"):
                query = mp.get("memory_content", "")
                _, mem_list, search_ms = await adapter.search_memory(query, user_id, top_k=10)
                total_search_ms += search_ms
                # Format as strings: "timestamp: text" (evaluation.py expects str)
                mp["memories_from_system"] = [
                    f"{ts}: {text}" if ts else text
                    for ts, text in mem_list[:20]
                ]

        # ── Op 3: Question Answering ──
        output_questions = []
        for q in questions:
            question_text = q.get("question", "")
            context, _, search_ms = await adapter.search_memory(question_text, user_id, top_k=20)
            total_search_ms += search_ms

            response, resp_ms = await adapter.answer_question(question_text, context)
            total_response_ms += resp_ms

            output_questions.append({
                "question": q.get("question", ""),
                "answer": q.get("answer", ""),
                "evidence": q.get("evidence", []),
                "difficulty": q.get("difficulty", ""),
                "question_type": q.get("question_type", ""),
                "context": context,
                "search_duration_ms": round(search_ms, 2),
                "system_response": response,
                "response_duration_ms": round(resp_ms, 2),
            })

        output_sessions.append({
            "memory_points": memory_points,
            "dialogue": dialogue,
            "extracted_memories": extracted,
            "add_dialogue_duration_ms": round(add_ms, 2),
            "questions": output_questions if output_questions else [],
        })

        if (idx + 1) % 10 == 0:
            logger.info("  Session %d/%d done (sem=%d entries, epi=%d entries)",
                        idx + 1, len(sessions),
                        adapter.semantic.count(),
                        adapter.episodic.count())

    # Final consolidation (skip if consolidate_every is very high = disabled)
    if run_consolidation_every < 999999:
        await adapter.run_consolidation()

    result = {
        "uuid": user_data.get("uuid", ""),
        "user_name": user_name,
        "sessions": output_sessions,
        "timing": {
            "total_extraction_ms": round(total_extraction_ms, 2),
            "total_search_ms": round(total_search_ms, 2),
            "total_response_ms": round(total_response_ms, 2),
        },
    }

    logger.info("User %s done: %d sessions, %d memories, %d QA",
                user_name, len(sessions),
                adapter.semantic.count(),
                len([q for s in output_sessions for q in s.get("questions", [])]))

    return result


async def main():
    parser = argparse.ArgumentParser(description="HaluMem Benchmark — EXIA GHOST")
    parser.add_argument("--users", type=int, default=1, help="Number of users to process (1-20)")
    parser.add_argument("--dry", action="store_true", help="Dry run (no LLM calls for QA)")
    parser.add_argument("--consolidate-every", type=int, default=10,
                        help="Run consolidation every N sessions")
    parser.add_argument("--no-consolidation", action="store_true",
                        help="Disable consolidation entirely (benchmark mode)")
    args = parser.parse_args()

    # Load dataset
    if not DATASET_PATH.exists():
        logger.error("Dataset not found: %s", DATASET_PATH)
        sys.exit(1)

    users = []
    with open(DATASET_PATH) as f:
        for line in f:
            users.append(json.loads(line))
            if len(users) >= args.users:
                break

    logger.info("Loaded %d user(s) from %s", len(users), DATASET_PATH.name)

    # Setup
    embedder = Embedder()
    llm_fn = None
    if not args.dry:
        llm_fn = await create_haiku_fn()
        if llm_fn is None:
            logger.warning("No LLM available — running in dry mode")
            args.dry = True

    # Results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = RESULTS_DIR / f"{FRAME_NAME}_eval_results.jsonl"

    # Process each user with fresh ChromaDB
    all_results = []

    for i, user_data in enumerate(users):
        tmp_dir = tempfile.mkdtemp(prefix=f"halumem_user{i}_")
        logger.info("User %d/%d — ChromaDB: %s", i + 1, len(users), tmp_dir)

        adapter = ExiaGhostAdapter(
            chromadb_path=tmp_dir,
            embedder=embedder,
            llm_fn=llm_fn,
            dry_run=args.dry,
        )

        consolidate_every = 999999 if args.no_consolidation else args.consolidate_every
        result = await process_user(adapter, user_data, consolidate_every)
        all_results.append(result)

        # Cleanup ChromaDB
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Write results JSONL
    with open(output_file, "w") as f:
        for result in all_results:
            f.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")

    logger.info("Results saved: %s", output_file)

    # Print summary
    print("\n" + "=" * 60)
    print("HALUMEM BENCHMARK — EXIA GHOST V5")
    print("=" * 60)
    for r in all_results:
        n_sessions = len(r["sessions"])
        n_memories = sum(len(s.get("extracted_memories", [])) for s in r["sessions"])
        n_qa = sum(len(s.get("questions", [])) for s in r["sessions"])
        timing = r.get("timing", {})
        print(f"\n  User: {r['user_name']}")
        print(f"  Sessions: {n_sessions}")
        print(f"  Memories extracted: {n_memories}")
        print(f"  QA answered: {n_qa}")
        print(f"  Extraction time: {timing.get('total_extraction_ms', 0):.0f}ms")
        print(f"  Search time: {timing.get('total_search_ms', 0):.0f}ms")
        print(f"  LLM time: {timing.get('total_response_ms', 0):.0f}ms")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
