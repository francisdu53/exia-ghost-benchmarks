"""
LoCoMo Benchmark — EXIA GHOST Adapter

Evaluates EXIA GHOST V5 on the LoCoMo benchmark (ACL 2024).
10 conversations, 2 speakers each, 1986 QA across 5 categories.

Usage:
  python eval_locomo.py                    # full run
  python eval_locomo.py --dry              # no LLM calls
  python eval_locomo.py --convs 2          # first 2 conversations only
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from exia.core.types import EpisodicEntry, SemanticEntry
from exia.memories.episodic import EpisodicMemory
from exia.memories.semantic import SemanticMemory
from exia.providers.embedder import Embedder

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
logger = logging.getLogger("locomo")
logger.setLevel(logging.INFO)

DATASET_PATH = Path(__file__).parent / "repo" / "data" / "locomo10.json"
RESULTS_DIR = Path(__file__).parent / "results" / "exiaghost-v5"


# ═══════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════

def _make_semantic(text, vector, user_id, timestamp_str, source_type="conversation"):
    return SemanticEntry(
        id=f"sem_{uuid.uuid4().hex[:12]}",
        concept=text[:100],
        definition=text,
        vector=vector,
        source=user_id,
        source_type=source_type,
        trust_level=0.8,
        learned_at=datetime.now(),
        usage_count=1,
        confidence=0.5,
        emotional_context=0.0,
        tags=[],
        user_id=user_id,
        privacy="normal",
    )


def _make_episodic(text, vector, user_id, timestamp_str):
    return EpisodicEntry(
        id=f"ep_{uuid.uuid4().hex[:12]}",
        content=text,
        context=f"locomo_{timestamp_str}",
        vector=vector,
        timestamp=datetime.now(),
        emotional_intensity=0.3,
        novelty=0.5,
        participants=["user"],
        user_id=user_id,
        privacy="normal",
        consolidated=False,
        faded=False,
    )


def _split_facts(text):
    """Split message into atomic sentences."""
    _NOISE = ("hello", "hi ", "hey", "thank", "sure", "of course", "ok",
              "yes", "no", "great", "good", "bye", "goodbye", "alright",
              "wow", "oh", "haha", "lol", "nice")
    if not text or len(text) < 15:
        return [text] if text and len(text.strip()) >= 10 else []
    parts = []
    for sep in (".", "!", "?", ";"):
        if sep in text:
            parts = [f.strip() for f in text.split(sep) if f.strip()]
            break
    if not parts:
        parts = [text.strip()]
    return [p for p in parts if len(p) >= 10 and not p.lower().startswith(_NOISE)]


# ═══════════════════════════════════════════════════════
# Extraction prompt
# ═══════════════════════════════════════════════════════

EXTRACTION_PROMPT = """You are a memory extraction system. Extract factual memories from the dialogue below.

# FORMAT RULES (CRITICAL):
- ALWAYS use third person: use speaker names (never "I", "my", "me")
- One memory per line
- Average length: 15-20 words per memory
- No numbering, no bullets, no prefixes

# MEMORY TYPES:
1. PERSONA: "[Name]'s [attribute] is [value]"
2. EVENT: "[Name] did/is/has [action or situation]"
3. RELATIONSHIP: "[Name]'s [relation] with [person], [description]"

# RULES:
- Include specific dates, names, locations when mentioned
- One fact per line — split compound sentences
- Do NOT invent or infer — extract only what is explicitly stated
- If no factual memories, write "NONE"

Dialogue:
{dialogue}

Extracted memories:"""


# ═══════════════════════════════════════════════════════
# QA prompt
# ═══════════════════════════════════════════════════════

QA_PROMPT = """You are a knowledgeable AI assistant with access to personal memories from two speakers in a conversation.

# INSTRUCTIONS:
1. Carefully analyze ALL provided memories from BOTH speakers. Synthesize information across multiple entries.
2. If memories contain contradictory information, the MOST RECENT memory (by timestamp) is the source of truth.
3. If the question involves relative time references ("last year", "two months ago"), calculate the actual date from the memory timestamp.
4. Your answer must be grounded in the memories. You may use general knowledge to interpret information found in memories.
5. Only say "Unknown" if the memories contain absolutely NO information related to the question. If partial information exists, answer with what you have.
6. CRITICAL: Your final answer MUST be under 5-6 words. No explanations, no justifications. Just the answer.

{speaker_a} memories:
{context_a}

{speaker_b} memories:
{context_b}

Question: {question}

Answer:"""


# ═══════════════════════════════════════════════════════
# Judge prompt (GPT-4o-mini)
# ═══════════════════════════════════════════════════════

JUDGE_PROMPT = """Your task is to label an answer to a question as 'CORRECT' or 'WRONG'.
You will be given: (1) a question, (2) a 'gold' answer, (3) a generated answer.
Be generous with grading — as long as it touches on the same topic as the gold answer, count as CORRECT.
For time-related questions, even different formats (e.g., "May 7th" vs "7 May") should be CORRECT.
If the gold answer indicates the information is not available and the generated answer also says unknown/not mentioned, mark as CORRECT.

Return ONLY a JSON object: {{"label": "CORRECT"}} or {{"label": "WRONG"}}

Question: {question}
Gold answer: {gold}
Generated answer: {response}"""


# ═══════════════════════════════════════════════════════
# Adapter
# ═══════════════════════════════════════════════════════

class LoCoMoAdapter:

    def __init__(self, chromadb_path, embedder, llm_fn=None, judge_fn=None,
                 dry_run=False):
        self.embedder = embedder
        self.semantic = SemanticMemory(chromadb_path, collection_name="locomo_sem")
        self.episodic = EpisodicMemory(chromadb_path, collection_name="locomo_epi")
        self.llm_fn = llm_fn
        self.judge_fn = judge_fn
        self.dry_run = dry_run

    def embed(self, text):
        return self.embedder.embed(text)

    async def ingest_session(self, turns, session_date, speaker_a, speaker_b,
                             uid_a, uid_b):
        """Ingest one session of dialogue into memory stores."""
        for turn in turns:
            text = turn.get("text", "")
            speaker = turn.get("speaker", "")
            if not text or len(text) < 10:
                continue

            uid = uid_a if speaker == speaker_a else uid_b

            # Sentence split + store in semantic
            sentences = _split_facts(text)
            for sentence in sentences:
                vector = self.embed(sentence)
                entry = _make_semantic(sentence, vector, uid, session_date)
                await self.semantic.store(entry, user_id=uid)

            # Full text in episodic
            vector = self.embed(text)
            entry = _make_episodic(text, vector, uid, session_date)
            await self.episodic.store(entry, user_id=uid)

        # LLM extraction (if available)
        if self.llm_fn and not self.dry_run:
            dialogue_text = "\n".join(
                f"[{session_date}] {t['speaker']}: {t['text']}"
                for t in turns if t.get("text")
            )
            try:
                raw = await self.llm_fn(
                    EXTRACTION_PROMPT.format(dialogue=dialogue_text)
                )
                for line in raw.strip().split("\n"):
                    line = line.strip().lstrip("- ").lstrip("• ").strip()
                    if line and line.upper() != "NONE" and len(line) > 10:
                        # Determine which speaker this fact belongs to
                        uid = uid_a if speaker_a.lower() in line.lower() else uid_b
                        vector = self.embed(line)
                        entry = _make_semantic(line, vector, uid, session_date,
                                              source_type="llm_extraction")
                        await self.semantic.store(entry, user_id=uid)
            except Exception as e:
                logger.warning("LLM extraction failed: %s", e)

    async def answer_question(self, question, uid_a, uid_b, speaker_a, speaker_b):
        """Search memories from both speakers and answer."""
        query_vec = self.embed(question)

        # Search both speakers
        sem_a = await self.semantic.retrieve(query_vec, mode="explore",
                                            top_k=15, user_id=uid_a)
        sem_b = await self.semantic.retrieve(query_vec, mode="explore",
                                            top_k=15, user_id=uid_b)

        context_a = "\n".join(
            f"- {r.data.get('definition', '')}" for r in sem_a
        ) or "- No memories found"

        context_b = "\n".join(
            f"- {r.data.get('definition', '')}" for r in sem_b
        ) or "- No memories found"

        if self.dry_run or self.llm_fn is None:
            return "[DRY RUN]", context_a, context_b

        prompt = QA_PROMPT.format(
            speaker_a=speaker_a, context_a=context_a,
            speaker_b=speaker_b, context_b=context_b,
            question=question,
        )

        response = await self.llm_fn(prompt)
        return response.strip(), context_a, context_b

    async def judge_answer(self, question, gold, response):
        """Use GPT-4o-mini to judge CORRECT/WRONG."""
        if self.dry_run or self.judge_fn is None:
            return "UNKNOWN"

        prompt = JUDGE_PROMPT.format(
            question=question, gold=gold, response=response
        )

        try:
            raw = await self.judge_fn(prompt)
            # Parse JSON
            import re
            match = re.search(r'"label"\s*:\s*"(CORRECT|WRONG)"', raw)
            if match:
                return match.group(1)
            return "UNKNOWN"
        except Exception as e:
            logger.warning("Judge failed: %s", e)
            return "UNKNOWN"


# ═══════════════════════════════════════════════════════
# LLM providers
# ═══════════════════════════════════════════════════════

async def create_haiku_fn():
    """Claude Haiku for extraction + QA."""
    try:
        from anthropic import AsyncAnthropic
        api_key = ""
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
            api_key = os.environ.get("EXIA_ANTHROPIC_API_KEY", "")

        if not api_key:
            return None

        client = AsyncAnthropic(api_key=api_key)

        async def generate(prompt):
            resp = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512, temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text

        logger.info("Haiku LLM ready")
        return generate
    except Exception:
        return None


async def create_judge_fn():
    """GPT-4o-mini for scoring."""
    try:
        from openai import AsyncOpenAI
        api_key = ""
        eval_env = Path(__file__).parent.parent / "halumem" / "repo" / "eval" / ".env"
        if eval_env.exists():
            for line in eval_env.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", "")

        if not api_key:
            return None

        client = AsyncOpenAI(api_key=api_key)

        async def judge(prompt):
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=50, temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content

        logger.info("GPT-4o-mini judge ready")
        return judge
    except Exception:
        return None


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════

async def process_conversation(adapter, conv_data, conv_idx):
    """Process one conversation: ingest + QA."""
    conv = conv_data["conversation"]
    speaker_a = conv["speaker_a"]
    speaker_b = conv["speaker_b"]
    uid_a = f"{speaker_a.lower()}_{conv_idx}"
    uid_b = f"{speaker_b.lower()}_{conv_idx}"

    # Get session keys sorted
    sessions = sorted([k for k in conv.keys()
                       if k.startswith("session_") and not k.endswith("_date_time")])

    logger.info("Conv %d: %s ↔ %s (%d sessions, %d QA)",
                conv_idx, speaker_a, speaker_b, len(sessions),
                len(conv_data.get("qa", [])))

    # Phase 1: Ingest
    t0 = time.perf_counter()
    for session_key in sessions:
        turns = conv[session_key]
        date_key = f"{session_key}_date_time"
        session_date = conv.get(date_key, "")
        await adapter.ingest_session(turns, session_date, speaker_a, speaker_b,
                                     uid_a, uid_b)

    ingest_ms = (time.perf_counter() - t0) * 1000
    logger.info("  Ingestion: %d sessions, sem=%d, epi=%d (%.0fms)",
                len(sessions), adapter.semantic.count(), adapter.episodic.count(),
                ingest_ms)

    # Phase 2: QA
    qa_results = []
    t0 = time.perf_counter()

    for qa in conv_data.get("qa", []):
        question = qa["question"]
        category = qa["category"]

        # Gold answer
        if category == 5:
            gold = "Not mentioned"
        else:
            gold = qa.get("answer", "")

        # Get answer from EXIA GHOST
        response, ctx_a, ctx_b = await adapter.answer_question(
            question, uid_a, uid_b, speaker_a, speaker_b
        )

        # Judge
        label = await adapter.judge_answer(question, gold, response)

        qa_results.append({
            "question": question,
            "gold": gold,
            "response": response,
            "category": category,
            "label": label,
            "evidence": qa.get("evidence", []),
        })

    qa_ms = (time.perf_counter() - t0) * 1000
    logger.info("  QA: %d questions answered (%.0fms)", len(qa_results), qa_ms)

    return {
        "conv_idx": conv_idx,
        "speaker_a": speaker_a,
        "speaker_b": speaker_b,
        "sessions": len(sessions),
        "qa_results": qa_results,
        "ingest_ms": round(ingest_ms, 2),
        "qa_ms": round(qa_ms, 2),
    }


async def main():
    parser = argparse.ArgumentParser(description="LoCoMo Benchmark — EXIA GHOST")
    parser.add_argument("--convs", type=int, default=10, help="Number of conversations (1-10)")
    parser.add_argument("--dry", action="store_true", help="Dry run (no LLM/judge calls)")
    args = parser.parse_args()

    if not DATASET_PATH.exists():
        logger.error("Dataset not found: %s", DATASET_PATH)
        sys.exit(1)

    with open(DATASET_PATH) as f:
        data = json.load(f)

    convs = data[:args.convs]
    logger.info("Loaded %d conversations from LoCoMo", len(convs))

    embedder = Embedder()
    llm_fn = None if args.dry else await create_haiku_fn()
    judge_fn = None if args.dry else await create_judge_fn()

    if not args.dry:
        if llm_fn is None:
            logger.warning("No Haiku — running extraction/QA in dry mode")
        if judge_fn is None:
            logger.warning("No GPT-4o-mini — running scoring in dry mode")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []

    for i, conv_data in enumerate(convs):
        tmp_dir = tempfile.mkdtemp(prefix=f"locomo_conv{i}_")

        adapter = LoCoMoAdapter(
            chromadb_path=tmp_dir,
            embedder=embedder,
            llm_fn=llm_fn,
            judge_fn=judge_fn,
            dry_run=args.dry,
        )

        result = await process_conversation(adapter, conv_data, i)
        all_results.append(result)

        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Aggregate scores
    scores_by_cat = {}
    total_correct = 0
    total_scored = 0

    for result in all_results:
        for qa in result["qa_results"]:
            cat = qa["category"]
            label = qa["label"]
            if cat not in scores_by_cat:
                scores_by_cat[cat] = {"correct": 0, "wrong": 0, "unknown": 0, "total": 0}
            scores_by_cat[cat]["total"] += 1
            if label == "CORRECT":
                scores_by_cat[cat]["correct"] += 1
                total_correct += 1
            elif label == "WRONG":
                scores_by_cat[cat]["wrong"] += 1
            else:
                scores_by_cat[cat]["unknown"] += 1
            total_scored += 1

    cat_names = {1: "multi-hop", 2: "temporal", 3: "world-knowledge",
                 4: "single-hop", 5: "adversarial"}

    output = {
        "benchmark": "LoCoMo",
        "system": "EXIA GHOST V5",
        "timestamp": datetime.now().isoformat(),
        "conversations": len(convs),
        "total_qa": total_scored,
        "total_correct": total_correct,
        "overall_accuracy": round(total_correct / total_scored, 4) if total_scored > 0 else 0,
        "category_scores": {},
        "results": all_results,
    }

    for cat in sorted(scores_by_cat.keys()):
        s = scores_by_cat[cat]
        acc = s["correct"] / s["total"] if s["total"] > 0 else 0
        output["category_scores"][f"cat{cat}_{cat_names.get(cat, 'unknown')}"] = {
            "accuracy": round(acc, 4),
            "correct": s["correct"],
            "wrong": s["wrong"],
            "unknown": s["unknown"],
            "total": s["total"],
        }

    # Save
    out_file = RESULTS_DIR / "locomo_eval_results.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("LOCOMO BENCHMARK — EXIA GHOST V5")
    print("=" * 60)
    print(f"\nConversations: {len(convs)}")
    print(f"Total QA: {total_scored}")
    print(f"Overall accuracy: {output['overall_accuracy']:.2%}")
    print(f"\nPer category:")
    for cat_key, cat_data in output["category_scores"].items():
        print(f"  {cat_key}: {cat_data['accuracy']:.2%} "
              f"({cat_data['correct']}/{cat_data['total']})")
    print(f"\nResults: {out_file}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
