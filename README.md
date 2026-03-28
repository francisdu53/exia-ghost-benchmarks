# EXIA GHOST — Cognitive Memory Architecture for AI Agents

> A bio-inspired cognitive architecture that remembers, reasons, and resists hallucinations.

---

## Results at a Glance

### Public Benchmarks

| Benchmark | Score | Details |
|-----------|-------|---------|
| **LoCoMo** (ACL 2024) — Full Pipeline | **95.27%** accuracy (cats 1-5) | 10 conversations, 1,986 QA, 20 speakers |
| **LoCoMo** Cat 5 (adversarial) | **100.00%** | Zero hallucination on 446 adversarial questions |
| **LoCoMo** — Memory Baseline | **89.94%** accuracy (cats 1-4) | Same dataset, memory-only (no cognitive pipeline) |
| **HaluMem** (arXiv 2511.03506) | **F1 71.99%** | First independent evaluation of this benchmark |
| **HaluMem** Precision | **92.90%** | When EXIA extracts a fact, it is correct 93% of the time |
| **HaluMem** Update Hallucination | **1.41%** | Near-zero hallucination on memory updates |

### Competitive Landscape (as of March 2026)

> The following comparison reflects publicly available scores at the time of publication.
> These results are subject to change as competitors update their systems.

| System | LoCoMo | HaluMem F1 | Cat 5 (adversarial) | Total Funding |
|--------|--------|-----------|---------------------|---------------|
| **EXIA GHOST Full** | **95.27%** | **71.99%** | **100.00%** | **$0** |
| EverMemOS | 92.32% | — | skipped | Shanda Group |
| MemU | 92.09% | — | skipped | — |
| MemMachine v0.2 | 91.23% | — | skipped | $43.5M |
| EXIA GHOST Memory | 89.94% | 71.99% | 71.52% | $0 |
| MemMachine v0.1 | 84.87% | — | skipped | — |
| MemOS | — | 79.70%* | — | $0 (academic) |
| Memobase | 75.78% | — | skipped | No disclosed funding |
| Zep | 58.44–75.14%* | < 50% | skipped | $2.3M |
| Mem0 | 66.9% | 57.85% | skipped | $24M |
| Supermemory | — | 56.90% | skipped | Google execs |

\* MemOS and HaluMem share 7 authors — self-evaluation. See [note below](#note-on-halumem-benchmark-independence).

### LoCoMo — Full Pipeline Results (10 conversations, 1,986 QA)

| Category | Accuracy | Correct / Total |
|----------|----------|-----------------|
| **Overall (cats 1-5)** | **95.27%** | **1,892 / 1,986** |
| Cat 1 — Multi-hop reasoning | **96.81%** | 273 / 282 |
| Cat 2 — Temporal reasoning | **99.07%** | 318 / 321 |
| Cat 3 — World knowledge | 92.71% | 89 / 96 |
| Cat 4 — Single-hop retrieval | 91.08% | 766 / 841 |
| Cat 5 — Adversarial (abstention) | **100.00%** | 446 / 446 |

Full Pipeline: proprietary cognitive architecture with bio-inspired memory processing.
**First and only system to achieve 100% on Category 5 (zero hallucination on adversarial questions).**

### LoCoMo — Memory Baseline Results (10 conversations, 1,540 QA cats 1-4)

| Category | Accuracy | Correct / Total |
|----------|----------|-----------------|
| Overall (cats 1-4) | 89.94% | 1,385 / 1,540 |
| Cat 5 — Adversarial | 71.52% | 319 / 446 |

Memory-only configuration without the cognitive pipeline.

### HaluMem — Detailed Results (1 user, 65 sessions)

| Metric | Score |
|--------|-------|
| F1 Extraction | **71.99%** |
| Precision | **92.90%** |
| Recall | 58.76% |
| Memory Update — Correct | **77.46%** |
| Memory Update — Hallucination | **1.41%** |
| QA — Correct | 58.54% |

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

- **QA Generation**: Claude Haiku 4.5 (answers ≤ 5-6 words)
- **HaluMem Judge**: GPT-4o (official benchmark standard)
- **LoCoMo Judge**: GPT-4o-mini (standard used by Mem0/MemMachine)
- **Memory Backend**: ChromaDB with 384-dim MiniLM embeddings
- **Extraction**: Sentence splitting + inline deduplication + LLM extraction
  (atomic facts in third person)
- **Cat 5 Included**: Unlike all competitors, we evaluate adversarial questions

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
