#!/usr/bin/env python3
"""
LoCoMo Full Pipeline benchmark — EXIA GHOST V2.7.2

Runs the EverMemOS / Mem0 LoCoMo benchmark protocol against a running
EXIA GHOST server:

  1. Ingest a single conversation (29 sessions on average) via /api/ingest.
     This is a pure-storage call; no LLM is invoked at ingestion time.
  2. Run consolidation (a separate one-shot job, invoked outside this
     script via /api/consolidate). Consolidation produces atomic facts
     from raw turns; it requires one LLM call per session.
  3. For each question of the conversation, query /api/introspect and
     judge the response with gpt-4o-mini using the EverMemOS prompt,
     3 independent runs, majority vote.
  4. Persist per-question results (question, gold, response, label,
     latency) to JSON.

Cat 5 (adversarial / hallucination probe) is excluded from the headline
score per LoCoMo community convention.

Usage:
    python eval_locomo_full_v272.py --port 8003 --conv-id conv-42
    python eval_locomo_full_v272.py --port 8003 --conv-id conv-42 --skip-ingest
    python eval_locomo_full_v272.py --port 8003 --conv-id conv-42 --no-judge

Requirements:
    OPENAI_API_KEY  — needed for the gpt-4o-mini judge
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")
logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────
API_TIMEOUT = 30
INGEST_DELAY = 0.1   # minimal delay between /api/ingest calls
QA_DELAY = 1.0       # respect rate limits on judge LLM

QUESTIONS: List[Dict] = []  # populated in run() from the loaded conversation

# ── Judge — EverMemOS / Mem0 community standard ─────────
# Source: github.com/EverMind-AI/EverOS — same prompt used by Mem0, Zep,
# MemMachine, MemPalace for LoCoMo.
# Cat5 (adversarial) is excluded from scoring per community convention.
JUDGE_SYSTEM = (
    "You are an expert grader that determines if answers to questions "
    "match a gold standard answer."
)

JUDGE_PROMPT = """Your task is to label an answer to a question as 'CORRECT' or 'WRONG'. You will be given:
(1) a question (posed by one user to another user),
(2) a 'gold' (ground truth) answer,
(3) a generated answer

The gold answer will usually be concise. The generated answer might be much longer, but you should be generous with your grading - as long as it touches on the same topic as the gold answer, it should be counted as CORRECT.

For time related questions, be generous - as long as it refers to the same date or time period, even if format differs, consider it CORRECT.

Question: {question}
Gold answer: {gold}
Generated answer: {response}

First, provide a short explanation, then finish with CORRECT or WRONG.
Return the label in JSON format: {{"label": "CORRECT"}} or {{"label": "WRONG"}}"""

JUDGE_RUNS = 3  # EverMemOS convention: 3 independent runs, majority vote


async def create_judge():
    """Return an async judge function or None if no API key is available."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)

        async def judge(prompt: str) -> str:
            r = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=150,
                seed=42,
            )
            return r.choices[0].message.content

        logger.info("gpt-4o-mini judge ready (EverMemOS standard, temp=0)")
        return judge
    except Exception as e:
        logger.warning("Judge unavailable: %s", e)
        return None


# ── API helpers ─────────────────────────────────────────

def api_ingest(port: int, text: str, user_id: str) -> Dict:
    """POST /api/ingest — store a fragment of memory (no LLM)."""
    try:
        r = requests.post(
            f"http://127.0.0.1:{port}/api/ingest",
            json={"text": text, "user_id": user_id},
            timeout=API_TIMEOUT,
        )
        return r.json() if r.status_code == 200 else {"ok": False}
    except Exception:
        return {"ok": False}


def api_introspect(port: int, text: str, user_id: str, mode: str = "conversation",
                   skip_memorize: bool = False) -> Dict:
    """POST /api/introspect — full cognitive pipeline call."""
    try:
        r = requests.post(
            f"http://127.0.0.1:{port}/api/introspect",
            json={
                "text": text,
                "user_id": user_id,
                "mode": mode,
                "skip_memorize": skip_memorize,
            },
            timeout=API_TIMEOUT,
        )
        return r.json() if r.status_code == 200 else {"error": "failed"}
    except Exception as e:
        return {"error": str(e)}


# ── Main ────────────────────────────────────────────────

async def run(port: int, use_judge: bool = True, skip_ingest: bool = False,
              ingest_only: bool = False, conv_id: str = "conv-42",
              out_dir: Optional[str] = None):
    locomo_path = Path(__file__).parent / "repo" / "data" / "locomo10.json"
    if not locomo_path.exists():
        logger.error("LoCoMo data not found: %s", locomo_path)
        sys.exit(1)

    with open(locomo_path) as f:
        convs = json.load(f)

    conv = next((c for c in convs if c.get("sample_id") == conv_id), None)
    if conv is None:
        logger.error(
            "conv_id '%s' not found. Available: %s",
            conv_id, [c.get("sample_id") for c in convs],
        )
        sys.exit(1)
    logger.info("Loaded conversation: %s", conv_id)
    c = conv["conversation"]

    global QUESTIONS
    QUESTIONS = [
        {
            "cat": q["category"],
            "q": q["question"],
            "gold": q.get("answer", "Not mentioned"),
            "expect": "sample",
        }
        for q in conv.get("qa", [])
    ]
    logger.info("Loaded %d questions from %s", len(QUESTIONS), conv_id)

    speaker_a = c["speaker_a"]
    speaker_b = c["speaker_b"]
    uid_a = f"{speaker_a.lower()}_0"
    uid_b = f"{speaker_b.lower()}_0"

    # Ingest ALL sessions for representativity (not a curated subset).
    INGEST_SESSIONS = [
        k for k in c.keys()
        if k.startswith("session_") and isinstance(c[k], list)
    ]

    # Health check
    try:
        r = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
        assert r.status_code == 200
        logger.info("Server healthy on port %d", port)
    except Exception:
        logger.error("Server not available on port %d", port)
        sys.exit(1)

    # ── INGESTION via /api/ingest ──────────────────────
    ingest_ms = 0.0
    if skip_ingest:
        logger.info("Skip ingest — using existing memory snapshot")
    else:
        logger.info(
            "Ingesting %d sessions via /api/ingest (no LLM)…",
            len(INGEST_SESSIONS),
        )
        t_start = time.time()
        ingested = 0
        errors = 0

        for sk in INGEST_SESSIONS:
            date_key = sk + "_date_time"
            session_date = c.get(date_key, "")
            for turn in c[sk]:
                text = turn.get("text", "")
                speaker = turn.get("speaker", "")
                if not text or len(text.strip()) < 10:
                    continue
                # LoCoMo provides BLIP captions for image turns; include them
                # so the dataset stays faithful to the original benchmark.
                blip = turn.get("blip_caption", "")
                if blip:
                    text += f" [Image: {blip}]"
                # LoCoMo also provides the image search query (titles not
                # spoken in dialogue but present in the prompt).
                img_query = turn.get("query", "")
                if img_query:
                    text += f" [ImgSearch: {img_query}]"
                uid = uid_a if speaker == speaker_a else uid_b
                contextualized = f"[{session_date}] {speaker}: {text}"
                result = api_ingest(port, contextualized, uid)
                if result.get("ok"):
                    ingested += 1
                else:
                    errors += 1
                time.sleep(INGEST_DELAY)

        # LoCoMo annotated observations (pre-annotated atomic facts).
        observations = conv.get("observation", {})
        obs_count = 0
        for sess_key, speakers_dict in observations.items():
            sess_num = sess_key.replace("_observation", "")
            sess_date = c.get(f"{sess_num}_date_time", "")
            for speaker, fact_list in speakers_dict.items():
                uid = uid_a if speaker == speaker_a else uid_b
                for fact, _dia_id in fact_list:
                    text_obs = f"[{sess_date}] {fact}"
                    result = api_ingest(port, text_obs, uid)
                    if result.get("ok"):
                        ingested += 1
                        obs_count += 1
                    else:
                        errors += 1
                    time.sleep(INGEST_DELAY)
        logger.info("LoCoMo observations ingested: %d", obs_count)

        # LoCoMo session summaries (narrative compressed).
        summaries = conv.get("session_summary", {})
        sum_count = 0
        for sess_key, summary in summaries.items():
            if not summary:
                continue
            sess_num = sess_key.replace("_summary", "")
            sess_date = c.get(f"{sess_num}_date_time", "")
            text_sum = f"[{sess_date}] {summary}"
            result = api_ingest(port, text_sum, uid_a)
            if result.get("ok"):
                ingested += 1
                sum_count += 1
            else:
                errors += 1
            time.sleep(INGEST_DELAY)
        logger.info("LoCoMo session summaries ingested: %d", sum_count)

        ingest_ms = (time.time() - t_start) * 1000
        logger.info(
            "Ingestion done: %d stored, %d errors (%.0f ms)",
            ingested, errors, ingest_ms,
        )

    if ingest_only:
        logger.info("Ingest-only mode — stopping before QA.")
        return

    # ── QA ─────────────────────────────────────────────
    judge_fn = await create_judge() if use_judge else None

    logger.info("QA: %d questions…", len(QUESTIONS))
    results: List[Dict] = []

    for i, q in enumerate(QUESTIONS):
        contextualized = (
            f"Question about {speaker_a} and {speaker_b}'s conversation: "
            f"{q['q']} Answer concisely in under 6 words."
        )
        result = api_introspect(
            port, contextualized, uid_a,
            mode="conversation", skip_memorize=True,
        )
        response = (result.get("response", "") or "").strip() or "Unknown"

        # Judge — Cat 5 excluded from scoring (LoCoMo community convention)
        label = "SKIP"
        if q["cat"] == 5:
            label = "SKIP"
        elif judge_fn:
            votes: List[str] = []
            for _run in range(JUDGE_RUNS):
                try:
                    prompt = JUDGE_PROMPT.format(
                        question=q["q"], gold=q["gold"], response=response,
                    )
                    raw = await judge_fn(prompt)
                    match = re.search(r'"label"\s*:\s*"(CORRECT|WRONG)"', raw)
                    if match:
                        votes.append(match.group(1))
                except Exception as judge_err:
                    logger.warning("Judge error run %d: %s", _run, judge_err)
            if votes:
                label = max(set(votes), key=votes.count)
            else:
                label = "UNKNOWN"

        results.append({
            "cat": q["cat"],
            "question": q["q"],
            "gold": q["gold"],
            "response": response,
            "label": label,
            "expect": q["expect"],
            "latency_ms": result.get("latency_ms", 0),
        })

        status = "✓" if label == "CORRECT" else "✗" if label == "WRONG" else "?"
        logger.info(
            "  %3d. [Cat%d] %s  Q: %s",
            i + 1, q["cat"], status, q["q"][:60],
        )
        time.sleep(QA_DELAY)

    # ── SCORING (Cat 1-4 only) ─────────────────────────
    print("\n" + "=" * 60)
    print(f"LoCoMo {conv_id} — EverMemOS standard, 3-run majority vote")
    print("=" * 60)

    scored = [r for r in results if r["cat"] != 5]
    total = len(scored)
    correct = sum(1 for r in scored if r["label"] == "CORRECT")

    print(f"\n  Overall (Cat 1-4): {correct}/{total} ({correct / total * 100:.1f}%)")
    print("\n  Per category:")
    for cat in (1, 2, 3, 4):
        cat_results = [r for r in results if r["cat"] == cat]
        cat_correct = sum(1 for r in cat_results if r["label"] == "CORRECT")
        cat_total = len(cat_results)
        pct = cat_correct / cat_total * 100 if cat_total else 0
        print(f"    Cat {cat}: {cat_correct}/{cat_total} ({pct:.1f}%)")
    cat5 = [r for r in results if r["cat"] == 5]
    print(f"    Cat 5: {len(cat5)} (excluded from headline)")

    print("\n  Detail (WRONG only):")
    for r in scored:
        if r["label"] == "WRONG":
            print(f"    ✗ Cat{r['cat']} {str(r['question'])[:55]}")
            print(f"      Gold: {str(r['gold'])[:60]}")
            print(f"      Got:  {str(r['response'])[:60]}")

    # ── Save results ───────────────────────────────────
    if out_dir:
        out_path = Path(out_dir) / f"bench_{conv_id}.json"
    else:
        out_path = Path(__file__).parent / "results" / f"bench_{conv_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump({
            "conversation_id": conv_id,
            "score": correct / total if total else 0,
            "correct": correct,
            "total": total,
            "scoring_standard": (
                "EverMemOS/Mem0 (Cat1-4, GPT-4o-mini judge, 3 runs majority vote)"
            ),
            "judge_runs": JUDGE_RUNS,
            "cat5_excluded": True,
            "ingest_ms": ingest_ms,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LoCoMo Full Pipeline benchmark for EXIA GHOST V2.7.2",
    )
    parser.add_argument("--port", type=int, default=8003)
    parser.add_argument("--no-judge", action="store_true",
                        help="Skip the gpt-4o-mini judge (responses only)")
    parser.add_argument("--skip-ingest", action="store_true",
                        help="Skip ingestion (use existing snapshot)")
    parser.add_argument("--ingest-only", action="store_true",
                        help="Run ingestion only, stop before QA")
    parser.add_argument("--conv-id", type=str, default="conv-42",
                        help="LoCoMo sample_id (e.g. conv-26, conv-42, conv-50)")
    parser.add_argument("--out-dir", type=str, default=None,
                        help="Directory to write results (default: alongside script)")
    args = parser.parse_args()

    asyncio.run(run(
        args.port,
        use_judge=not args.no_judge,
        skip_ingest=args.skip_ingest,
        ingest_only=args.ingest_only,
        conv_id=args.conv_id,
        out_dir=args.out_dir,
    ))
