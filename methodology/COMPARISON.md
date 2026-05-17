# Detailed Comparison — EXIA GHOST vs Competitors

> All data as of May 2026. Self-reported scores have not been independently audited unless
> explicitly noted. Subject to change as systems evolve.

## LoCoMo Benchmark (ACL 2024)

| System | Overall (Cat 1-4) | Evaluation | Source / Note |
|--------|-------------------|------------|---------------|
| MemMachine v0.2 (gpt-4.1-mini) | 91.69% | Self-reported | [memmachine.ai](https://memmachine.ai/blog/2025/12/memmachine-v0.2-delivers-top-scores-and-efficiency-on-locomo-benchmark/) |
| EverMemOS | 92.32% | Self-reported | [EverMemOS evaluation](https://github.com/EverMind-AI/EverMemOS/blob/main/evaluation/README.md) |
| MemU | 92.09% | Self-reported | [memu.pro](https://memu.pro/benchmark) |
| ByteRover 2.0 | 92.2% | Self-reported | [byterover.dev](https://www.byterover.dev/blog/benchmark-ai-agent-memory) |
| Mem0 (latest, 2025) | 91.6 – 92.5% | Self-reported | [mem0.ai/research](https://mem0.ai/research) |
| **EXIA GHOST Memory Baseline** | **89.94%** | Self-reported, raw data published | [this repo](../locomo/) |
| **EXIA GHOST Full Pipeline V2.7.2** | **84.16%** | Self-reported, raw data published | [`locomo/RESULTS_FULL_PIPELINE_V272.md`](../locomo/RESULTS_FULL_PIPELINE_V272.md) |
| MemMachine v0.1 | 84.87% | Self-reported | their first paper |
| Memori Labs | 81.95% | Self-reported | [memorilabs.ai](https://memorilabs.ai/blog/memori-locomo-paper-results/) |
| LangMem | 78.05% | Cross-evaluation by Memori | [memorilabs.ai](https://memorilabs.ai/blog/memori-locomo-paper-results/) |
| Memobase | 75.78% overall / 85.1% temporal | Self-reported | [memobase.io](https://www.memobase.io/blog/ai-memory-benchmark) |
| Zep | 75.14% (counter-claim) / 58.44% (audit by Mem0) / 84% (original retracted) | **Disputed** | [Issue #5 on zep-papers](https://github.com/getzep/zep-papers/issues/5) |
| Pam | 74.35% | Self-reported | [Pam blog](https://manager.harmix.ai/blog/pam-locomo-benchmark-results) |
| Letta | 74.0% | Self-reported | [letta.com](https://www.letta.com/blog/benchmarking-ai-agent-memory) |
| Mem0 (ECAI 2025 paper) | 66.9% | Independent paper | [arXiv 2504.19413](https://arxiv.org/abs/2504.19413) |
| OpenAI Memory | 52.9% | Cross-evaluation by Mem0 | Mem0 paper |

**Notes on the LoCoMo competitive landscape :**

- **Almost every score above is self-reported** by the system vendor on their own
  infrastructure. Independent cross-evaluation is rare.
- The benchmark itself has been audited :
  [Penfield Labs found that 6.4 % of LoCoMo gold answers are wrong](https://dev.to/penfieldlabs/we-audited-locomo-64-of-the-answer-key-is-wrong-and-the-judge-accepts-up-to-63-of-intentionally-33lg)
  and that the judge LLM accepts up to 63 % of intentionally wrong answers. **A single
  absolute LoCoMo score is therefore not a reliable ranking signal.** What matters more is
  methodology, raw data availability, and reproducibility.
- EXIA GHOST publishes (a) raw per-question JSON for every conversation, (b) a clean-room
  reproducibility protocol, and (c) cross-version reproducibility evidence (V2.7.0 → V2.7.2,
  one month apart, identical 158 / 199 strict on `conv-42`).
- EXIA GHOST publishes **two** numbers because the configurations measure different things :
  - **Memory Baseline (89.94 %)** = memory-only configuration, comparable to what most
    competitors report.
  - **Full Pipeline V2.7.2 (84.16 %)** = the integrated cognitive system under strict
    constraints (cognitive contract enforced, Cat 5 abstention, no silent fallback). Lower
    number, real number.
- Cat 5 (adversarial) is excluded from the headline per EverMemOS / Mem0 community
  convention. EXIA GHOST tracks Cat 5 separately as a hallucination-resistance metric.
- The retracted EXIA GHOST Full result (95.27 %, April 2026) has been removed from this
  table. The story is documented in the README "Correction Note" section and at
  [`locomo/RESULTS_FULL_PIPELINE_V272.md`](../locomo/RESULTS_FULL_PIPELINE_V272.md).

## HaluMem Benchmark (arXiv 2511.03506)

| System | F1 Extraction | Precision | Recall | Update Correct | Update Hallucination | QA Correct | Evaluation |
|--------|--------------|-----------|--------|---------------|---------------------|-----------|------------|
| MemOS | 79.70% | — | — | — | — | — | Self-evaluation* |
| **EXIA GHOST** | **71.99%** | **92.90%** | **58.76%** | **77.46%** | **1.41%** | **58.54%** | Independent |
| Mem0-Graph | 57.85% | — | — | — | — | — | By HaluMem team |
| Supermemory | 56.90% | — | — | — | — | — | By HaluMem team |
| Zep | < 50% | — | — | — | — | — | By HaluMem team |

\* MemOS and HaluMem share 7 authors — self-evaluation.

**Notes:**
- EXIA GHOST is the only system with full metric breakdown published
- EXIA GHOST is the first independent evaluation of HaluMem
- All other scores come from the HaluMem paper (tested by benchmark authors)

## Internal Benchmarks (EXIA GHOST only)

No competitor publishes equivalent internal benchmark data.

| Capability | EXIA GHOST Result | Competitors |
|-----------|------------------|-------------|
| Pipeline latency (p99) | **2.37ms** (budget 50ms) | Not published |
| Hallucination rate (multi-LLM) | **0%** across 6 providers | Not published |
| Long-term recall (96 exchanges) | **92.9%** exact | Not published |
| Jailbreak resistance | **0% bypass**, 6 strategies | Not published |
| Graceful degradation | **5/5** fail-closed | Not published |
| Consciousness metrics | **13/13** axes validated | Not published |
| Emotional processing | **4/5** criteria | Not published |
| Contradiction detection (F1) | **92.31%** | Not published |
| Multi-user validation | **20 speakers**, 0 errors | Not published |

## Architecture Comparison

| Feature | EXIA GHOST | Mem0 | Zep | MemMachine |
|---------|-----------|------|-----|------------|
| Cognitive pipeline (< 50ms) | ✓ | ✗ | ✗ | ✗ |
| Cognitive Contract (structural LLM control) | ✓ | ✗ | ✗ | ✗ |
| Ethical Guardian (fail-closed) | ✓ | ✗ | ✗ | ✗ |
| Inline deduplication (real-time) | ✓ | ✗ | ✗ | ? |
| NLI contradiction detection | ✓ | ✗ | ✗ | ✗ |
| Multi-user native | ✓ | ✓ | ✓ | ✓ |
| LLM-agnostic (6 providers validated) | ✓ | Partial | Partial | Partial |
| Bio-inspired forgetting | ✓ | ✗ | ✗ | ✗ |
| Consciousness metrics | ✓ | ✗ | ✗ | ✗ |
| Category 5 (adversarial) published | ✓ | ✗ | ✗ | ✗ |
| Open benchmark reproduction | ✓ | Partial | ✓ | ✗ |

## Cost Comparison

| System | Benchmark cost | Infrastructure |
|--------|---------------|----------------|
| **EXIA GHOST** | **~$1** (LoCoMo), **~$10** (HaluMem) | 2 vCPU, 8 GB RAM |
| Mem0 | Not disclosed | Cloud API |
| Zep | Not disclosed | Cloud API |
| MemMachine | Not disclosed | MacBook Pro M3 (reported) |

EXIA GHOST runs complete public benchmarks for under $15 total on a $10/month VPS.
