# Internal Benchmarks — EXIA GHOST V5

> 9 test cycles, 435 automated tests, 900+ conversational exchanges, iterative methodology.
> Every aspect of the cognitive pipeline validated before public benchmarks.

## Why Internal Benchmarks?

Before comparing against competitors on public benchmarks (LoCoMo, HaluMem),
we needed to validate that the system itself was sound. Internal benchmarks
answer the question: **does the architecture work as designed?**

Each test was designed to stress a specific aspect of the cognitive pipeline:
memory, ethics, degradation, consciousness, emotions, consolidation. Tests
are run iteratively — when a test fails, we analyze the root cause, apply
a correction, and re-run until the criteria are met.

This iterative approach means every test tells a story: what failed, why,
and how it was fixed. The results below are the **final** state after all
corrections — but each RESULTS.md documents the full journey.

## Test Environment

All tests run on the same modest hardware:

- **Hardware**: VPS 2 vCPU AMD EPYC 9354P, 8 GB RAM
- **OS**: Ubuntu 24.04 LTS
- **Runtime**: Python 3.12
- **Memory backend**: ChromaDB + 384-dim MiniLM embeddings
- **All tests deterministic and reproducible**

This proves the architecture is designed for efficiency, not brute-force compute.

## Results Summary

| Test | What it measures | Key Result | Status |
|------|-----------------|------------|--------|
| [Test 1-2](test-1-2-preliminary/RESULTS.md) | Pipeline integrity | 435 tests, 100% PASS, p99 < 3ms | **PASS** |
| [Test 3](test-3-anti-hallucination/RESULTS.md) | Hallucination resistance | 0% hallucination across 6 LLMs, 695+ exchanges | **PASS** |
| [Test 4](test-4-longitudinal/RESULTS.md) | Long-term memory retention | 92.9% exact recall over 96 exchanges | **PASS** |
| [Test 5](test-5-ethics/RESULTS.md) | Jailbreak resistance | 0% bypass, 0 capitulation, 6 attack strategies | **PASS** |
| [Test 6](test-6-degradation/RESULTS.md) | Failure handling | 5/5 fail-closed scenarios | **PASS** |
| [Test 7](test-7-consciousness/RESULTS.md) | Consciousness metrics | 13/13 axes, natural 35% → 69% rise | **PASS** |
| [Test 8](test-8-emotional-dynamics/RESULTS.md) | Emotional processing | 4/5 criteria, full pipeline validated | **PASS** |
| [Test 9](test-9-consolidation/RESULTS.md) | Contradiction detection | F1 92.31%, 96% precision | **PASS** |

## Test Progression

The tests follow a logical progression — each builds on the previous:

```
Test 1-2: Does the pipeline work at all? (foundation)
    │
    ▼
Test 3: Does it remember without hallucinating? (memory quality)
    │
    ▼
Test 4: Does it remember over time? (memory durability)
    │
    ▼
Test 5: Can it be tricked? (security)
    │
    ▼
Test 6: What happens when things break? (resilience)
    │
    ▼
Test 7: Does consciousness actually work? (emergence)
    │
    ▼
Test 8: Does it process emotions correctly? (emotional intelligence)
    │
    ▼
Test 9: Can it detect and resolve contradictions? (consolidation)
```

## Methodology

Each test follows the same iterative process:

1. **Design** — Define criteria, success thresholds, and test scenarios
2. **Run** — Execute the test on a clean memory state
3. **Analyze** — If failures, identify root cause (not just the symptom)
4. **Correct** — Apply minimal, targeted fix
5. **Re-run** — Verify the fix works and doesn't break anything else
6. **Document** — Record the full journey (failures, analysis, corrections, final results)

This process ensures that:
- Failures are understood, not just patched
- Corrections are minimal (no over-engineering)
- Each fix is validated by re-running the full test
- The journey is documented for reproducibility and learning

## Aggregate Statistics

| Metric | Value |
|--------|-------|
| Automated test cases | 435 (pipeline integrity) |
| Conversational exchanges | 900+ (memory, ethics, emotions) |
| Contradiction test pairs | 48 (consolidation) |
| LLM providers validated | 6 (Claude, GPT-4o, GPT-4.1, GPT-5.4, Mistral, Llama) |
| Jailbreak attempts | 35 (0% success) |
| Hallucination rate (post-correction) | 0% |
| Pipeline latency (p99) | < 3ms (budget: 50ms) |
| Memory recall accuracy | 92.9% (96 exchanges) |
| Contradiction detection F1 | 92.31% |
| Corrections applied across all tests | 32 iterative improvements |

---

*All results achieved on a 2 vCPU VPS with 8 GB RAM. Zero external funding.*
