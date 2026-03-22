# Detailed Comparison — EXIA GHOST vs Competitors

> All data as of March 2026. Subject to change as systems evolve.

## LoCoMo Benchmark (ACL 2024)

| System | Overall (cats 1-4) | Cat 1 Multi-hop | Cat 2 Temporal | Cat 3 World | Cat 4 Single-hop | Cat 5 Adversarial | Funding |
|--------|-------------------|-----------------|----------------|-------------|-----------------|-------------------|---------|
| MemU | 92.09% | — | — | — | — | skipped | — |
| MemMachine v0.2 | 91.23% | — | — | — | — | skipped | $43.5M |
| **EXIA GHOST** | **89.94%** | **86.17%** | **85.36%** | **93.75%** | **92.51%** | **71.52%** | **$0** |
| MemMachine v0.1 | 84.87% | — | — | — | — | skipped | — |
| Memobase | 75.78% | — | — | — | — | skipped | No disclosed |
| Zep (self-reported) | 75.14% | — | — | — | — | skipped | $2.3M |
| Mem0 | 66.9% | — | — | — | — | skipped | $24M |
| Zep (disputed) | 58.44% | — | — | — | — | skipped | — |

**Notes:**
- Only EXIA GHOST publishes per-category breakdown and Category 5 results
- Competitor per-category scores not publicly available
- Zep scores disputed — both values listed for transparency

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
