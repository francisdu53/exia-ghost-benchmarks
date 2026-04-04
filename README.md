# EXIA GHOST — Cognitive Memory Architecture for AI Agents

> A bio-inspired cognitive architecture that remembers, reasons, and resists hallucinations.

---

## Results at a Glance

### Public Benchmarks

| Benchmark | Score | Details |
|-----------|-------|---------|
| **HaluMem** (arXiv 2511.03506) | **F1 82.10%** | **#1 worldwide** — First independent evaluation |
| **HaluMem** Precision | **90.45%** | When EXIA extracts a fact, it is correct 90% of the time |
| **HaluMem** Update Hallucination | **0.00%** | Zero hallucination on memory updates |
| **LoCoMo** (ACL 2024) — Memory Baseline | **89.94%** accuracy (cats 1-4) | 10 conversations, 1,986 QA, 20 speakers |
| **LoCoMo** — Full Pipeline | Re-run in progress | Previous result retracted — see [correction note](#correction-note-locomo-full-pipeline) |

### Competitive Landscape (as of April 2026)

> The following comparison reflects publicly available scores at the time of publication.
> These results are subject to change as competitors update their systems.

| System | HaluMem F1 | LoCoMo | Total Funding |
|--------|-----------|--------|---------------|
| **EXIA GHOST** | **82.10%** | **89.94%** | **$0** |
| MemOS | 79.70%* | — | $0 (academic) |
| EverMemOS | — | 93% | Shanda Group |
| MemMachine v0.2 | — | 91.23% | $43.5M |
| Memobase | — | 75.78% | No disclosed funding |
| Mem0 | 57.85% | 66.9% | $24M |
| Zep | < 50% | 58.44–75.14% | $2.3M |
| Supermemory | 56.90% | — | Google execs |

\* MemOS and HaluMem share 7 authors — self-evaluation. See [note below](#note-on-halumem-benchmark-independence).

### HaluMem — Detailed Results (V1.3.2, 1 user, 65 sessions)

| Metric | Score |
|--------|-------|
| F1 Extraction | **82.10%** |
| Precision | **90.45%** |
| Recall | **75.17%** |
| Memory Update — Correct | **35.21%** |
| Memory Update — Hallucination | **0.00%** |
| QA — Correct | 57.32% |
| QA — Hallucination | 13.41% (estimated real: ~2.4%) |

Judge: GPT-4o. Calibrated against GPT-4o-mini (F1 delta < 2%).
Full analysis: [HALUMEM_V132_EN_ANALYSIS.md](halumem/HALUMEM_V132_EN_ANALYSIS.md)

### LoCoMo — Memory Baseline Results (10 conversations, 1,540 QA cats 1-4)

| Category | Accuracy | Correct / Total |
|----------|----------|-----------------|
| Overall (cats 1-4) | **89.94%** | 1,385 / 1,540 |
| Cat 5 — Adversarial | 71.52% | 319 / 446 |

Memory-only configuration without the cognitive pipeline.
Evaluation code published: [`eval_locomo.py`](locomo/eval_locomo.py)

### Correction Note: LoCoMo Full Pipeline

> **April 2026**: The previously published Full Pipeline score (95.27%) has been retracted.
> Investigation revealed that a software bug (graceful degradation mode triggering on excessive
> cognitive latency) caused the pipeline to return template responses ("Not mentioned") instead
> of actual cognitive answers. Combined with LLM judge leniency on template responses, this
> produced artificially inflated scores. The bug has been identified and fixed in V1.4.1.
> A corrected Full Pipeline re-run is in progress and results will be published with raw
> per-question data for full independent verification.
>
> The Memory Baseline score (89.94%) is unaffected — it uses published evaluation code
> and produces real factual answers.
>
> We thank [@dial481](https://github.com/dial481/locomo-audit) for the thorough audit
> that helped identify this issue.

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
