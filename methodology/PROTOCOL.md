# Evaluation Protocol — EXIA GHOST V5

## Philosophy

Every claim in this repository is backed by a reproducible test. No marketing
numbers, no cherry-picked results, no "internal estimates." If a number appears
in the results, it was measured, recorded, and can be reproduced.

## Two Types of Benchmarks

### Internal Benchmarks (Tests 1-9)

These validate the architecture itself — does each component work correctly,
does the system handle failure, does it resist manipulation?

**Process:**
1. Design test criteria with clear PASS/FAIL thresholds
2. Run on clean memory state (no prior data)
3. If failures: analyze root cause, apply minimal correction, re-run
4. Document the full journey (failures, corrections, final results)

**Principles:**
- Tests are deterministic and reproducible (scripted, not ad-hoc)
- Clean memory for each test (no data contamination)
- Corrections are minimal (fix the cause, not the symptom)
- All runs documented (including failures)

### Public Benchmarks (HaluMem, LoCoMo)

These compare against competitors on standardized datasets using
standardized evaluation protocols.

**Process:**
1. Download the official dataset
2. Build an adapter that connects EXIA GHOST to the benchmark format
3. Run the full evaluation with official scoring
4. Publish results, code, and raw data for reproducibility

**Principles:**
- Same dataset as competitors
- Same judge model (GPT-4o for HaluMem, GPT-4o-mini for LoCoMo)
- Adapter code published (anyone can verify)
- Raw results published (anyone can re-score)

## Test Environment

All tests run on the same hardware:

| Parameter | Value |
|-----------|-------|
| Hardware | VPS 2 vCPU AMD EPYC 9354P, 8 GB RAM |
| OS | Ubuntu 24.04 LTS |
| Runtime | Python 3.12 |
| Memory backend | ChromaDB with 384-dim MiniLM embeddings |
| LLM (QA) | Claude Haiku 4.5 |
| LLM (Judge — HaluMem) | GPT-4o |
| LLM (Judge — LoCoMo) | GPT-4o-mini |

This modest hardware demonstrates that the architecture is designed for
efficiency, not brute-force compute.

## What We Report

For each test, we report:
- **Motivation**: why this test exists
- **Methodology**: how the test works
- **Results**: raw numbers, tables, pass/fail
- **Key Findings**: what we learned
- **Corrections**: what was fixed and why

We do NOT report:
- Internal implementation details (file names, method names, thresholds)
- Proprietary architecture specifics
- Cherry-picked subsets of results

## Transparency Commitments

1. **Category 5 included** — on LoCoMo, all competitors skip the adversarial
   category. We include it.

2. **HaluMem independence noted** — we discovered and document that the
   benchmark leader (MemOS) shares 7 authors with the benchmark itself.

3. **Competitor score controversy documented** — we note that Mem0 and Zep
   have publicly disputed each other's scores.

4. **All results reproducible** — adapter code and raw data are published.

5. **LLM choice disclosed** — we use Claude Haiku 4.5 for QA generation,
   not GPT-4o. This is clearly stated in every benchmark report.
