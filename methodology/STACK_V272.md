# EXIA GHOST V2.7.2 — Public Stack

This document lists the **publicly-disclosed stack** used for the V2.7.2 LoCoMo Full Pipeline benchmark. It enables an external reviewer to reproduce the environment.

Architectural details (cognitive pipeline structure, memory stores, retrieval primitives, symbolic guards) are intentionally not disclosed pending patent filing.

---

## 1. Runtime

| Component | Version |
|---|---|
| OS | Linux x86_64 (Ubuntu) |
| Python | 3.12 |
| PyTorch | 2.10.0 |
| FastAPI | 0.135.1 |
| Uvicorn | 0.41.0 |
| Pydantic | 2.12.5 |
| PyYAML | 6.0.3 |
| requests | 2.32.5 |
| APScheduler | ≥ 3.10 |

The full pinned `requirements.txt` is published alongside the benchmark for reproducibility.

---

## 2. Vector store

| Component | Version | Role |
|---|---|---|
| ChromaDB | 1.5.2 | Persistent vector store (cosine similarity) |
| SQLite FTS5 | bundled | Lexical retrieval (BM25) |

No FAISS, no Milvus, no Weaviate. ChromaDB + FTS5 BM25 are sufficient at the scale we benchmarked.

---

## 3. Embeddings

| Model | Dimension | Role |
|---|---|---|
| `BAAI/bge-m3` | 1024 | Primary embedder (V2.7.0+) |
| sentence-transformers wrapper | 5.2.3 | Loader |
| numpy | 2.4.2 | Tensors |
| safetensors | 0.7.0 | Secure weights format |

Earlier versions used `all-mpnet-base-v2` (768 dim) — replaced by BGE-m3 for stronger multilingual retrieval and consistent performance on out-of-distribution queries.

---

## 4. LLM strategy — strict 2-LLM count

| Role | Model | Provider | Status |
|---|---|---|---|
| Verbalizer | `gpt-4.1-mini` | OpenAI | active |
| Consolidator | `gpt-4.1-mini` | OpenAI | active |
| Any 3rd LLM | — | — | **forbidden by design** |

The cognitive pipeline calls **at most two LLMs per interaction**. There is no third LLM for routing, classification, intent detection, or any other purpose — everything else is symbolic (regex, embeddings, small specialized transformers, lookup tables).

**Why this matters** : a higher LLM count means more latency, higher cost, and a larger attack surface for prompt injection and hallucination cascades. The 2-LLM ceiling is an architectural commitment, not a budget choice.

The benchmark judge `gpt-4o-mini` is **external** to the system under test — it is the LoCoMo scoring infrastructure, not part of EXIA GHOST.

Fallback LLM providers are configured (Mistral, Anthropic) but inactive in the V2.7.2 benchmark.

---

## 5. Specialized transformers (non-LLM)

| Model | Role | Status V2.7.2 |
|---|---|---|
| `cross-encoder/nli-deberta-v3-base` | NLI ensemble (contradiction detection) | active |
| `cross-encoder/nli-deberta-v3-small` | NLI dedup | active |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder reranker | **disabled** in V2.7.2 |
| `cross-encoder/ms-marco-MiniLM-L-12-v2` | Reranker alternative | cached, not used |
| `mixedbread-ai/mxbai-rerank-large-v1` | Reranker alternative | cached, not used |

The reranker is intentionally disabled in V2.7.2 — symbolic retrieval handles ranking without an additional ML pass.

---

## 6. NLP

| Component | Version | Role |
|---|---|---|
| spaCy | 3.8.11 | NER (model: `fr_core_news_sm`) |
| KeyBERT | bundled | Concept tagging at ingestion |
| Custom triplet extractor | in-house | regex (pass 1) + spaCy NER (pass 2) for PERSON / LOC / ORG / DATE |

Note : the spaCy model is the French small model, while LoCoMo is in English. This means NER on the LoCoMo dataset is sub-optimal — a known limitation tracked for V3.0.0 (either switch to `en_core_web_sm` or remove the NER pass entirely).

---

## 7. Persistence

| Element | Backend |
|---|---|
| Vector embeddings | ChromaDB (filesystem) |
| Lexical index | SQLite FTS5 |
| Audit / journal | SQLite |
| Traces | JSONL daily files |

All persistent state is on local disk. No cloud-side memory storage.

---

## 8. Hardware

| | Specification |
|---|---|
| Environment | Single VPS (Hostinger) |
| CPU | shared multi-core |
| GPU | none (CPU-only inference) |
| RAM | 16 GB |

Benchmarks were run on CPU only. BGE-m3 inference on CPU is the dominant per-query cost on this hardware.

---

## 9. Benchmark protocol

The clean-room protocol applied per conversation :

1. Stop any running server.
2. Purge all memory stores.
3. Restore the post-ingest + post-consolidation snapshot for that conversation.
4. Export required environment variables (OpenAI API key for the judge).
5. Boot the server and wait for `/health` to return 200.
6. Run all 4 categories of questions for the conversation through `/api/introspect`.
7. Score each question via the `gpt-4o-mini` judge (3 runs majority vote).
8. Persist results to JSON.

No state carries over between conversations.

---

## 10. Reproducibility evidence

| | Date | Score (conv-42, strict) |
|---|---|---|
| V2.7.0 | April 2026 | 158 / 199 |
| V2.7.2 | May 2026 | 158 / 199 |

Aggregate identical across one month. One question's verdict swapped between runs, consistent with documented `gpt-4o-mini` judge non-determinism (~ 1 in 200 at `temperature=0.0`). No silent drift in the pipeline.

---

## 11. What is intentionally not disclosed

- Architecture of the cognitive pipeline (stage names, ordering, internal contracts).
- Memory store taxonomy and lifecycles.
- Scoring primitives and exact retrieval weights.
- The deterministic symbolic safety layer's rule set.
- Internal causal-reasoning structures.
- Prompt templates used in consolidation and verbalization.

This information will be published once the patent application has been filed. The benchmark is **fully reproducible** without these internals — given the same dataset, same model versions, and the clean-room protocol described above, an external reviewer can re-run the system and re-score independently.
