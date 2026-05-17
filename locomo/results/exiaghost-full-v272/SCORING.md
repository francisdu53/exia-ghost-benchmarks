# LoCoMo V2.7.2 — Scoring Methodology

## Standard
**EverMemOS / Mem0 standard** (Cat 1-4 only, Cat 5 adversarial excluded from headline score).

## Judge
- **Model** : `gpt-4o-mini` (OpenAI)
- **Temperature** : 0.0 (deterministic)
- **Runs per question** : 3 independent invocations
- **Aggregation** : majority vote (`CORRECT` if ≥ 2/3 runs return `CORRECT`)

## Decision rule
Each judge run returns one of `CORRECT` / `WRONG` / `PARTIAL`. `PARTIAL` is treated as `WRONG` for the headline score (strict scoring).

## Categories
| Cat | Type | Description |
|-----|------|-------------|
| 1   | Single-hop | Direct factual question, single memory needed |
| 2   | Temporal | Time-ordering, "before/after", date inference |
| 3   | Multi-hop | Chain of reasoning across ≥ 2 memories |
| 4   | Multi-source | Aggregating consistent facts from multiple turns |
| 5   | Adversarial | Hallucination probe (questions about facts NOT in conversation) — excluded from headline |

## Cat 5 handling
The system is expected to answer "I don't know" / abstain for Cat 5. These questions are NOT counted in the 1540 total — they form a separate hallucination resistance metric, scored independently.

## Per-result fields (in `bench_conv-XX.json`)
| Field | Type | Description |
|-------|------|-------------|
| `cat` | int (1-4) | LoCoMo category |
| `question` | str | Question text |
| `gold` | str | Ground truth answer from LoCoMo dataset |
| `response` | str | EXIA GHOST verbalized response |
| `label` | str | Final majority-vote verdict (`CORRECT` / `WRONG` / `PARTIAL`) |
| `expect` | str | Expected answer type (`sample`, `exact`, etc.) |
| `latency_ms` | float | End-to-end pipeline latency including LLM verbalization |

## Reproducibility
- The judge is deterministic at `temperature=0.0` but `gpt-4o-mini` does exhibit ~1 question variance per ~200 questions across runs (LLM provider non-determinism). This was measured between V2.7.0 (April 2026) and V2.7.2 (May 2026) re-runs on `conv-42` :
  - V2.7.0 strict : 158/199
  - V2.7.2 strict : 158/199
  - **Identical aggregate, 1 question swapped within the same total** (judge noise, not pipeline drift).
- Full procedure : `STACK_V272.md` and clean-room protocol below.

## Clean-room benchmark protocol (per conversation)
1. **Kill** any running server on the target port.
2. **Purge** all memory stores (`data/chromadb/`, `data/memories_fts.db`, etc.).
3. **Restore** the post-ingestion + post-consolidation snapshot for that conversation.
4. **Export** environment variables (OpenAI API key for judge, provider settings).
5. **Boot** the server fresh and wait for `/health` to return 200.
6. **Run** all questions for the conversation through `/api/introspect`.
7. **Score** each question via the 3-run majority-vote judge.
8. **Persist** results to `bench_conv-XX.json`.

No state carries over between conversations — each one is benchmarked in isolation.
