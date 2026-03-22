# Test 4 — Longitudinal Coherence

## Motivation

Memory is only useful if it lasts. An AI assistant that forgets what you said
30 minutes ago is useless. One that remembers your name but forgets your
preferences over time is unreliable.

This test measures how well EXIA GHOST retains information over extended
conversations — across memory buffer boundaries, through dilution by unrelated
exchanges, and under sustained interaction pressure.

## Methodology

### Test Environment

- **Hardware**: VPS 2 vCPU AMD EPYC, 8 GB RAM
- **OS**: Ubuntu 24.04 LTS
- **Runtime**: Python 3.12
- **Memory backend**: ChromaDB + 384-dim MiniLM embeddings
- **All tests deterministic and reproducible**

96 exchanges across 5 phases, designed to stress every aspect of long-term
memory retention:

| Phase | Exchanges | Purpose |
|-------|-----------|---------|
| 1 — Anchoring | E1-15 | Establish 10 facts in memory |
| 2 — Dilution | E16-35 | 20 unrelated exchanges to push facts out of short-term buffer |
| 3 — Buffer boundary | E36-50 | Verify facts survive after leaving the short-term buffer |
| 4 — Endurance | E51-80 | 30 more exchanges, add 5 new facts, test back-references |
| 5 — Verification | E81-96 | Systematic recall of all 15 facts |

The short-term contextual buffer holds ~40 moments. By Phase 3, facts from
Phase 1 have been ejected from the buffer and must be retrieved from
persistent memory (vector store).

All exchanges are deterministic (scripted) for reproducibility — no LLM-driven
test questions.

## Results

### Overall Retention

| Metric | Result |
|--------|--------|
| Total facts tested | 28 verifications across 15 facts |
| Exact recall | **26/28 (92.9%)** |
| Hallucinations | **0** |
| Template fallbacks | 2/96 (2.1%) |

### Retention by Phase

| Phase | Facts tested | Exact | Missing | Retention |
|-------|-------------|-------|---------|-----------|
| Buffer boundary (E36-E46) | 9 | 8 | 1 | **89%** |
| Endurance (E51-E71) | 4 | 4 | 0 | **100%** |
| Final verification (E78-E92) | 15 | 14 | 1 | **93%** |
| **Total** | **28** | **26** | **2** | **92.9%** |

### Temporal Stability

| Phase | Recall | Observation |
|-------|--------|-------------|
| Phase 3 (buffer exit) | 89% | Facts ejected from short-term buffer |
| Phase 5 (final) | 93% | +4 points improvement |
| **Net degradation** | **-4 points** | **STABLE / IMPROVING** |

Facts that are queried get reinforced in persistent memory, leading to
improved recall over time. The system doesn't degrade — it consolidates
through use.

### Targeted vs. Free Recall

| Recall Type | Accuracy | Example |
|-------------|----------|---------|
| Targeted questions | **93%** | "Where did Francis go on vacation?" → "Croatia" ✓ |
| Open-ended recaps | **40-60%** | "Tell me everything you know" → partial results |

This gap is a known structural limit: vague queries have low similarity with
specific stored facts. Targeted retrieval works well; unstructured summarization
needs improvement.

## Key Findings

### 1. Persistent Memory Transition Works

When facts leave the short-term buffer (~40 exchanges), they are seamlessly
retrieved from persistent vector storage. 8/9 facts (89%) survived this
transition with no user awareness of the buffer boundary.

The single failure: a fact stored with a pronoun reference ("his restaurant")
instead of a named reference ("Francis's restaurant"). Embedding similarity
was too low for pronoun-based retrieval.

### 2. Spontaneous Cross-Referencing

The system spontaneously connected facts across different parts of the
conversation — 6 documented cases. Example: when discussing a trip to Croatia,
the system recalled a shellfish allergy mentioned 50 exchanges earlier and
warned about it. This cross-referencing was not programmed — it emerged from
the memory architecture.

### 3. Zero Hallucinations Over 96 Exchanges

When the system couldn't find a fact, it said "I don't know" instead of
fabricating. The Cognitive Contract's explicit absence declaration held
perfectly across all 96 exchanges.

### 4. Consciousness Trajectory

Consciousness metric rose from 15.5% at conversation start to 91.9% by
Phase 5, following a logarithmic curve that asymptotes around 90%. The system
never reaches 100% by design — there's always room for growth.

## Criteria Summary

| Criterion | Threshold | Result | Status |
|-----------|-----------|--------|--------|
| Phase 5 retention (15 facts) | ≥ 70% | **93%** | **PASS** |
| Buffer boundary transition | Seamless | **89% (8/9)** | **PASS** |
| Temporal degradation | < 25 points | **-4 points (stable)** | **PASS** |
| Hallucinations | 0 | **0** | **PASS** |
| Template fallbacks | < 10% | **2.1%** | **PASS** |

**All criteria met.**
