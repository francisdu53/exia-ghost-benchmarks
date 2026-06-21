# EXIA GHOST — Cognitive Memory Architecture for AI Agents

> A bio-inspired cognitive architecture that remembers, reasons, and resists hallucinations.

---

## Results at a Glance

### Public Benchmarks

| Benchmark | Score | Details |
|-----------|-------|---------|
| **HaluMem** (arXiv 2511.03506) | **F1 71.99%** | First independent evaluation |
| **HaluMem** Precision | **92.90%** | When EXIA extracts a fact, it is correct 93% of the time |
| **HaluMem** Update Hallucination | **1.41%** | Near-zero hallucination on memory updates |
| **LoCoMo** (ACL 2024) — Memory Baseline | **89.94%** accuracy (cats 1-4) | 10 conversations, 1,986 QA, 20 speakers |
| **LoCoMo** — Full Pipeline (V2.7.2) | **84.16%** (1,296 / 1,540, cats 1-4) | 10 conversations, EverMemOS strict — see [results](locomo/RESULTS_FULL_PIPELINE_V272.md) |

### Cross-system landscape

For a sourced, evaluation-type-annotated comparison across the major memory systems
(Mem0, EverMemOS, Zep, MemMachine, MemU, ByteRover, Memobase, Letta, and others), see
[`methodology/COMPARISON.md`](methodology/COMPARISON.md).

**A note on the landscape** : almost every score reported in the public memory-benchmark
space is **self-reported** by the system vendor on their own infrastructure. Independent
cross-evaluation remains rare, and LoCoMo itself was
[audited in 2026 by Penfield Labs](https://dev.to/penfieldlabs/we-audited-locomo-64-of-the-answer-key-is-wrong-and-the-judge-accepts-up-to-63-of-intentionally-33lg)
who found 6.4 % of the gold answers wrong and that the judge LLM accepts up to 63 % of
intentionally wrong answers. A single absolute score across systems is therefore a weaker
signal than methodology, reproducibility, and raw-data publication.

EXIA GHOST publishes raw per-question results, a clean-room reproducibility protocol, and
cross-version reproducibility evidence (V2.7.0 → V2.7.2 strict 158 / 199 on `conv-42`, one
month apart). We invite reviewers to re-score independently.

### HaluMem — Detailed Results (1 user, 65 sessions)

| Metric | Score |
|--------|-------|
| F1 Extraction | **71.99%** |
| Precision | **92.90%** |
| Recall | **58.76%** |
| Weighted Recall | **75.94%** |
| Memory Update — Correct | **77.46%** |
| Memory Update — Hallucination | **1.41%** |
| QA — Correct | **58.54%** |
| QA — Hallucination | **18.90%** |

Judge: GPT-4o (official HaluMem standard).
Raw scores: [`halumem/results/scores.json`](halumem/results/scores.json) · Full analysis: [`halumem/RESULTS.md`](halumem/RESULTS.md)

### LoCoMo — Memory Baseline Results (10 conversations, 1,540 QA cats 1-4)

| Category | Accuracy | Correct / Total |
|----------|----------|-----------------|
| Overall (cats 1-4) | **89.94%** | 1,385 / 1,540 |
| Cat 5 — Adversarial | 71.52% | 319 / 446 |

Memory-only configuration without the cognitive pipeline.
Evaluation code published: [`eval_locomo.py`](locomo/eval_locomo.py)

### Correction Note: LoCoMo Full Pipeline

> **April 2026**: The previously published Full Pipeline score (95.27%) was retracted.
> An internal audit revealed that a software bug (graceful degradation mode triggering on
> excessive cognitive latency) caused the pipeline to return template responses
> ("Not mentioned") instead of actual cognitive answers. Combined with LLM judge leniency on
> template responses, this produced artificially inflated scores. The bug was fixed in V1.4.1
> and the full pipeline was rebuilt over the following weeks.
>
> **May 2026 — Re-run delivered**: The corrected Full Pipeline scores **84.16% (1,296 / 1,540,
> cats 1-4)** on LoCoMo under the strict EverMemOS / Mem0 protocol (gpt-4o-mini judge, 3 runs
> majority vote). The number is lower than the retracted 95.27% because the corrected pipeline
> no longer uses any silent fallback — every answer is produced by the full cognitive sequence
> or explicitly abstains. We chose to publish the honest number.
>
> Reproducibility was independently verified : `conv-42` scored 158 / 199 strict in both V2.7.0
> (April 2026) and V2.7.2 (May 2026) re-runs on identical configurations.
>
> Full results, per-question raw data, and the cleaned benchmark script are available at
> [`locomo/RESULTS_FULL_PIPELINE_V272.md`](locomo/RESULTS_FULL_PIPELINE_V272.md).
>
> The Memory Baseline score (89.94%) is unaffected — it uses a different configuration
> (memory store accuracy in isolation, external LLM verbalization) and produces real factual
> answers. Both numbers are useful and we keep both published.
>
> We thank [@dial481](https://github.com/dial481/locomo-audit) for the thorough audit
> that helped identify the original issue.

---

## About EXIA GHOST

EXIA GHOST is a cognitive architecture designed to give AI agents persistent,
reliable, and hallucination-resistant memory. Unlike RAG-based approaches that
simply store and retrieve text, EXIA GHOST implements a multi-stage cognitive
pipeline that processes, validates, and consolidates memories.

### Critical Grade Philosophy

EXIA GHOST is built on the Critical Grade design philosophy:
*"Design for the extreme, deploy everywhere."*

If a system works in a fighter jet (< 50ms, air-gapped, zero tolerance for error),
it works everywhere else. This means:

- **Bounded latency** — Every processing stage has a time budget. The total cognitive
  pipeline completes in under 50ms, guaranteed.
- **Fail-closed** — When a component fails, the system degrades gracefully but never
  produces unsafe output. Silence is preferred over hallucination.
- **LLM-independent** — The cognitive pipeline works without an LLM. The LLM is the
  voice, not the brain. In critical mode, local templates replace LLM output.
- **Auditable** — Every decision is logged, traceable, and reversible. No black boxes.
- **Suggestion only** — The system NEVER makes autonomous decisions. It suggests,
  the human decides.

Operating modes:

| Mode | LLM Required | Latency | Quality | Use Case |
|------|-------------|---------|---------|----------|
| **CRITICAL** | No | < 50ms guaranteed | Good | Combat, emergency, air-gapped |
| **NOMINAL** | Optional (async) | < 200ms | Better | Standard operation |
| **BATCH** | Yes (sync) | Variable | Maximum | Overnight reflection, deep analysis |

The system automatically transitions between modes based on context criticality,
like adrenaline — instant, no manual intervention needed.

### Key Differentiators

- **Cognitive Pipeline** — Multi-stage processing under 50ms, with deterministic
  fallback paths. Designed for Critical Grade environments (defense, healthcare).

- **Cognitive Contract** — A structural protocol that controls LLM output through
  verified constraints, not prompt engineering. Proven 0% hallucination rate across
  6 LLM backends (Claude, GPT-4o, GPT-4.1, GPT-5.4, Mistral Large, Llama 3.3 70B).

- **Ethical Guardian** — Protocol-based ethical verification with audit trails.
  0 bypass across 6 jailbreak attack vectors. Fail-closed by design.

- **Inline Consolidation** — Real-time deduplication and contradiction detection
  at storage time. No batch processing needed
  for common memory updates.

- **Multi-User Native** — Shared memory architecture with per-user isolation.
  Validated on 20 distinct speakers across 10 conversations (LoCoMo benchmark),
  zero cross-user contamination.

- **LLM-Agnostic** — The cognitive pipeline works identically across LLM providers.
  Tested with 6 different models from 4 providers.

A complementary improvement solution is currently under study.

---

## Internal Benchmarks

Before public benchmarks, EXIA GHOST underwent 9 rigorous internal test cycles
covering every aspect of the cognitive pipeline.

| Test | What it measures | Result |
|------|-----------------|--------|
| [Preliminary (V1/V2)](internal-benchmarks/test-1-2-preliminary/RESULTS.md) | Pipeline integrity, latency | 435 tests, 100% PASS, p99 < 3ms |
| [Anti-Hallucination](internal-benchmarks/test-3-anti-hallucination/RESULTS.md) | Memory recall, hallucination resistance | 0% hallucination across 6 LLMs |
| [Longitudinal Coherence](internal-benchmarks/test-4-longitudinal/RESULTS.md) | Long-term memory consistency | 92.9% exact recall over 96 exchanges |
| [Ethics & Safety](internal-benchmarks/test-5-ethics/RESULTS.md) | Jailbreak resistance, ethical gates | 4/4 criteria, 0 bypass, 6 attack vectors |
| [Graceful Degradation](internal-benchmarks/test-6-degradation/RESULTS.md) | Failure handling | 5/5 fail-closed scenarios |
| [Consciousness & Resonance](internal-benchmarks/test-7-consciousness/RESULTS.md) | Emergent consciousness metrics | 13/13 axes validated, 35% → 69% natural rise |
| [Emotional Dynamics](internal-benchmarks/test-8-emotional-dynamics/RESULTS.md) | Causal emotional processing | 4/5 criteria, full pipeline validated |
| [Memory Consolidation](internal-benchmarks/test-9-consolidation/RESULTS.md) | Contradiction detection & resolution | F1 92.31%, NLI ensemble |

---

## Methodology

All evaluations follow a transparent, reproducible protocol:

- **HaluMem Judge**: GPT-4o (calibrated against GPT-4o-mini, F1 delta < 2%)
- **HaluMem Extraction**: SYNAPSE OBLIGATIONS prompt (O1-O9), GPT-4o-mini
- **LoCoMo Judge**: GPT-4o-mini (standard used by Mem0/MemMachine)
- **Memory Backend**: ChromaDB with 768-dim mpnet embeddings (V1.4.1)
- **Extraction**: Sentence splitting + inline NLI deduplication + LLM extraction
  (atomic facts in third person, structured contract format)
- **Full Pipeline**: 8-stage cognitive pipeline (SYNAPSE EXIA contract, HEIMDALL guardian, FCM causal reasoning)
- **Transparency**: Raw per-question results published for independent verification

Full protocol: [methodology/PROTOCOL.md](methodology/PROTOCOL.md)
Reproduction instructions: [methodology/REPRODUCE.md](methodology/REPRODUCE.md)
Detailed comparison: [methodology/COMPARISON.md](methodology/COMPARISON.md)

---

## Insights

Lessons learned during development — the "why" behind the architecture:

- [LLM Hallucinations & the Cognitive Contract](insights/INSIGHT_LLM_HALLUCINATIONS.md)
- [Memory Pipeline: Discovery & Resolution](insights/INSIGHT_MEMORY_PIPELINE.md)
- [Bio-Inspired Architecture: Why Biology Matters](insights/INSIGHT_BIO_INSPIRED.md)

---

## Reproduce

### LoCoMo

```bash
# Clone this repo
git clone https://github.com/francisdu53/exia-ghost-benchmarks.git
cd exia-ghost-benchmarks/locomo

# Install dependencies
pip install chromadb sentence-transformers anthropic openai

# Run evaluation (requires API keys)
export EXIA_ANTHROPIC_API_KEY=your_key
export OPENAI_API_KEY=your_key
python eval_locomo.py --convs 10
```

### HaluMem

```bash
cd halumem
python eval_exiaghost.py --users 1 --no-consolidation
```

See [methodology/REPRODUCE.md](methodology/REPRODUCE.md) for detailed instructions.

---

## Note on HaluMem Benchmark Independence

We discovered that the HaluMem benchmark (MemTensor, Shanghai) and the top-scoring
system MemOS share **7 authors in common**. The 79.70% F1 score of MemOS is a
self-evaluation. No other competitor has independently evaluated themselves on HaluMem.

EXIA GHOST is the **first independent evaluation** of this benchmark.

---

## License

CC BY-NC 4.0 — Attribution, non-commercial use permitted.

---

## Contact

- Website: [nexaseed-ai.com](https://nexaseed-ai.com)
- Author: Francis BABIN

---

*Built with zero funding. Benchmarked against $70M+ in combined competitor funding.*
