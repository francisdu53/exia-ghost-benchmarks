# LoCoMo Full Pipeline — V2.7.2 Results

**Version** : EXIA GHOST V2.7.2
**Date** : 10 May 2026
**Standard** : EverMemOS / Mem0 (Cat 1-4, `gpt-4o-mini` judge, 3 runs majority vote)
**Score** : **1296 / 1540 = 84.16 %**

---

## Headline result

| Metric | Value |
|---|---|
| Total questions (Cat 1-4) | **1540** |
| Total correct | **1296** |
| **Overall score** | **84.16 %** |
| Conversations | 10 / 10 (all of LoCoMo) |
| Configuration | Full cognitive pipeline (all stages enabled) |

This is the **corrected re-run** of the Full Pipeline configuration that we publicly retracted in April 2026 (see [Correction Note](#correction-note) below).

---

## Per-conversation breakdown

| Conversation | Correct / Total | Score | Cat 1 | Cat 2 | Cat 3 | Cat 4 |
|---|---|---|---|---|---|---|
| conv-26 | 128 / 152 | 84.2 % | 24/32 | 31/37 | 8/13 | 65/70 |
| conv-30 | 70 / 81 | 86.4 % | 9/11 | 25/26 | 0/0 | 36/44 |
| conv-41 | 132 / 152 | 86.8 % | 25/31 | 21/27 | 6/8 | 80/86 |
| conv-42 | 158 / 199 | 79.4 % | 20/37 | 38/40 | 4/11 | 96/111 |
| conv-43 | 150 / 178 | 84.3 % | 26/31 | 22/26 | 5/14 | 97/107 |
| conv-44 | 104 / 123 | 84.6 % | 23/30 | 21/24 | 2/7 | 58/62 |
| conv-47 | 127 / 150 | 84.7 % | 14/20 | 29/34 | 6/13 | 78/83 |
| conv-48 | 169 / 191 | 88.5 % | 18/21 | 36/42 | 6/10 | 109/118 |
| conv-49 | 124 / 156 | 79.5 % | 32/37 | 24/33 | 9/13 | 59/73 |
| conv-50 | 134 / 158 | 84.8 % | 26/32 | 25/32 | 5/7 | 78/87 |
| **TOTAL** | **1296 / 1540** | **84.16 %** | **217 / 282** | **272 / 321** | **51 / 96** | **756 / 841** |

---

## Per-category breakdown

| Category | Correct / Total | Score | Notes |
|---|---|---|---|
| **Cat 1** — Single-hop | 217 / 282 | **77.0 %** | Weakest; many single-hop questions actually require multi-hop reasoning under LoCoMo's labeling |
| **Cat 2** — Temporal | 272 / 321 | **84.7 %** | Strong on absolute-date questions, weaker on implicit ordering |
| **Cat 3** — Multi-hop | 51 / 96 | **53.1 %** | **Identified weakest category** — chain-of-reasoning over disjoint memories |
| **Cat 4** — Multi-source | 756 / 841 | **89.9 %** | **Strongest** — aggregating consistent facts across many turns |
| **Cat 5** — Adversarial | excluded from headline | — | Hallucination probe; tracked separately |

**Honest observation** — the 53.1 % on Cat 3 (multi-hop) is the largest known gap and is on our V2.8.0 roadmap. We chose to publish the strict score rather than re-label questions.

---

## Configuration

| Stack element | Version |
|---|---|
| Python | 3.12 |
| Vector store | ChromaDB 1.5.2 |
| Embedder | BGE-m3 (BAAI, 1024 dim) |
| Verbalizer LLM | `gpt-4.1-mini` (OpenAI) |
| Consolidation LLM | `gpt-4.1-mini` (OpenAI) |
| LLM count | **2 (strict)** |
| Cross-encoder reranker | disabled |
| NLI ensemble | `cross-encoder/nli-deberta-v3-base` + `-small` |
| NER | spaCy 3.8.11 + KeyBERT |
| Lexical retrieval | SQLite FTS5 BM25 |

Detailed stack : [`methodology/STACK_V272.md`](../methodology/STACK_V272.md)

---

## Differentiation from Memory Baseline (89.94 %)

We previously published a **Memory Baseline** result of 89.94 % (same LoCoMo). The two numbers come from **different configurations** and answer different questions :

| | Memory Baseline (89.94 %) | Full Pipeline V2.7.2 (84.16 %) |
|---|---|---|
| Scope | Memory store accuracy in isolation | Complete cognitive pipeline |
| LLM | External judge LLM verbalizes from raw memories | Internal 2-LLM strict (consolidation + verbalization) |
| Cognitive stages | none (direct retrieval) | full pipeline (perception → memorization) |
| Cognitive contract | none | enforced (action / boundaries / constraints) |
| Symbolic safety layer | none | active (deterministic ethical & contradiction gates) |
| Cat 5 handling | none | abstention enforced |
| What it measures | "is the right memory retrievable ?" | "does the cognitive system answer correctly under its own constraints ?" |

The Full Pipeline number is **stricter by design**. The cognitive contract explicitly forbids certain answer shapes (over-confident answers when memory is uncertain, mentioning entities not in the contract's scope, fabricating dates, etc.), which trades raw recall for **auditable, safe responses**.

We believe **both numbers are useful and honest** to publish. Memory Baseline shows the memory system's retrieval ceiling; Full Pipeline shows what the integrated cognitive system actually answers in production under its safety constraints.

---

## Reproducibility — V2.7.0 → V2.7.2

`conv-42` was independently re-benchmarked on the exact same configuration (same dataset, same code, same judge model, same clean-room protocol) one month apart :

| Version | Date | Score conv-42 |
|---|---|---|
| V2.7.0 | April 2026 | 158 / 199 |
| V2.7.2 | May 2026 | 158 / 199 |

**Aggregate identical (158/199 in both runs)**. A single question's verdict swapped between runs (a `WRONG` became `CORRECT`, a `CORRECT` became `WRONG`) — this is consistent with the documented `gpt-4o-mini` judge non-determinism (~ 1 question per 200 at `temperature=0.0` due to OpenAI provider noise). The pipeline itself is deterministic ; only the judge has residual stochasticity.

This rules out silent drift between V2.7.0 and V2.7.2.

---

## Where this places EXIA GHOST V2.7.2

The LoCoMo competitive landscape in May 2026 is heavily disputed.
Several systems (EverMemOS, MemMachine v0.2, MemU, ByteRover, recent
Mem0 releases) report **self-evaluated** scores above 90 % under
varying protocols. Some published numbers have been publicly contested
(e.g. Zep was audited from a claimed 84 % down to 58.44 %, then
counter-claimed 75.14 %).

LoCoMo itself was audited by Penfield Labs in 2026, who found that
**6.4 % of the gold answers are wrong** and that the judge LLM accepts
**up to 63 %** of intentionally wrong answers. So a single absolute
score on LoCoMo is not the right thing to optimize for — what matters
is the **methodology**, the **raw per-question data**, and the
**reproducibility**.

For context :

- Our **Memory Baseline (89.94 %, already published)** is a memory-only
  configuration comparable to what most competitors report. It sits in
  the competitive band.
- Our **Full Pipeline V2.7.2 (84.16 %)** is a strictly stricter test :
  the cognitive contract enforces abstention on adversarial questions,
  there is no silent fallback path, and every answer is produced by
  the full cognitive sequence or the system declines. It trades raw
  recall for **auditable, safe behavior**.

We publish both numbers because both are useful and honest. The
cross-system comparison table is maintained in
[`methodology/COMPARISON.md`](../methodology/COMPARISON.md) — single
source of truth, sourced per system, with evaluation type
(self-reported / audited / cross-evaluation) annotated for each row.

What we publish, that most competitors do not :

- Raw per-question JSON for every conversation (10 / 10).
- A clean-room reproducibility protocol.
- Cross-version reproducibility evidence (V2.7.0 → V2.7.2, one month
  apart, on identical configuration).
- An honest correction note for a previously-retracted result.

---

## What EXIA GHOST is

EXIA GHOST is a **cognitive middleware** : a deterministic decision layer that sits between an LLM and a user. The LLM verbalizes ; the cognitive pipeline decides, reasons causally, enforces ethical constraints, and produces a fully auditable trace of every decision.

It is **not** a RAG wrapper, a chatbot, a prompt-engineering trick, or a knowledge base. It is a separate system with its own state, memory model, and decision logic.

Architectural details (paradigms, memory stores, retrieval primitives, symbolic guards) are **deliberately not disclosed** in this benchmark publication while the corresponding patent application is being prepared. We commit to publishing a full technical paper once filing is complete.

What is disclosed here :
- The full set of benchmark results (per-question, per-category, per-conversation).
- The benchmark protocol (clean-room reproducibility procedure).
- The public stack (versions, models, providers).
- The honest delta between Memory Baseline and Full Pipeline configurations.

---

## Correction Note

In April 2026 we publicly retracted a previously-reported Full Pipeline score of **95.27 %** after an internal audit revealed that the configuration silently fell back to template-based responses (graceful degradation) on questions where the cognitive pipeline failed, inflating the apparent score.

The 84.16 % reported here is from the **corrected pipeline** with no silent fallback — every answer is produced by the full cognitive sequence or explicitly abstains. We chose to publish the corrected number even though it is lower, because it is the honest number.

This is the re-run we publicly committed to deliver. The raw per-question JSON files are in [`results/exiaghost-full-v272/`](results/exiaghost-full-v272/) so that any reviewer can re-score independently.

---

## Raw data & methodology

- Per-question results : [`results/exiaghost-full-v272/bench_conv-*.json`](results/exiaghost-full-v272/)
- Aggregated summary : [`results/exiaghost-full-v272/SUMMARY.json`](results/exiaghost-full-v272/SUMMARY.json)
- Scoring methodology : [`results/exiaghost-full-v272/SCORING.md`](results/exiaghost-full-v272/SCORING.md)
- Benchmark script : [`eval_locomo_full_v272.py`](eval_locomo_full_v272.py)
- Stack details : [`../methodology/STACK_V272.md`](../methodology/STACK_V272.md)

---

## Contact

For reproduction questions, methodology audit, or institutional inquiries :
GitHub : [@francisdu53](https://github.com/francisdu53)

---

*Published 17 May 2026.*
