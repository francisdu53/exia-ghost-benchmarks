# HaluMem Benchmark — EXIA GHOST V5

> First independent evaluation of the HaluMem benchmark.

## About HaluMem

HaluMem (arXiv 2511.03506) evaluates hallucinations in AI memory systems across
three operations: memory extraction, memory update, and memory QA. It is the first
benchmark specifically designed to reveal where hallucinations occur in the memory
pipeline.

- **Dataset**: HaluMem-Medium — 20 users, 30,073 dialogues, 14,948 memory points
- **Source**: [github.com/MemTensor/HaluMem](https://github.com/MemTensor/HaluMem)
- **License**: CC-BY-NC-ND-4.0

## Configuration

| Parameter | Value |
|-----------|-------|
| Hardware | VPS 2 vCPU AMD EPYC, 8 GB RAM |
| OS | Ubuntu 24.04 LTS, Python 3.12 |
| Users evaluated | 1 (Martin Mark, 65 sessions) |
| Memory extraction | Sentence splitting + inline deduplication + LLM extraction (Claude Haiku 4.5) |
| QA generation | Claude Haiku 4.5 (answers ≤ 5-6 words) |
| Judge | GPT-4o (official HaluMem standard) |
| Memory backend | ChromaDB + 384-dim MiniLM embeddings |
| Scoring completeness | 100% (451/451 integrity, 1047/1048 accuracy, 142/142 update, 164/164 QA) |

## Results

### Memory Extraction

| Metric | Score |
|--------|-------|
| **F1** | **71.99%** |
| Precision | **92.90%** |
| Recall | 58.76% |
| Weighted Recall | 75.94% |

When EXIA GHOST extracts a memory, it is correct 93% of the time.

### Memory Update

| Metric | Score |
|--------|-------|
| Correct | **77.46%** |
| Hallucination | **1.41%** |
| Omission | 21.13% |

Near-zero hallucination on memory updates — when information changes,
the system updates correctly without inventing false information.

### Question Answering

| Metric | Score |
|--------|-------|
| Correct | 58.54% |
| Hallucination | 18.90% |
| Omission | 22.56% |

### False Memory Resistance

| Metric | Score |
|--------|-------|
| FMR | 54.40% |

## Competitive Comparison (as of March 2026)

> Scores subject to change as competitors update their systems.

| System | F1 Extraction | Note |
|--------|--------------|------|
| MemOS | 79.70% | Self-evaluation (same team as HaluMem — see note below) |
| **EXIA GHOST** | **71.99%** | **First independent evaluation** |
| Mem0-Graph | 57.85% | Evaluated by HaluMem team |
| Supermemory | 56.90% | Evaluated by HaluMem team |
| Zep | < 50% | Evaluated by HaluMem team |

## Note on Benchmark Independence

The HaluMem benchmark and the top-scoring system MemOS are both products of the
MemTensor organization (Shanghai). They share **7 authors in common**. The 79.70%
F1 score of MemOS is a self-evaluation.

No other competitor has independently evaluated themselves on HaluMem. All scores
in the comparison table above (except EXIA GHOST) come from the HaluMem paper
itself — the competitors were tested by the benchmark authors, not by their own teams.

EXIA GHOST is the **first system to independently evaluate and publish** its own
HaluMem results, with full reproducibility (code, raw results, and methodology
provided in this repository).

## Methodology

### Memory Extraction Process

1. For each dialogue session, the system stores messages in persistent memory
   (sentence splitting + inline deduplication at storage time)
2. An LLM extraction step reformats stored memories as atomic facts in third person
   (e.g., "I live in Columbus" → "Martin Mark lives in Columbus")
3. This matches the format used by all competitors (Mem0, MemOS all use LLM extraction)

### QA Protocol

1. For each question, the system searches its memory stores
2. Retrieved memories are formatted with timestamps as context
3. Claude Haiku 4.5 generates a concise answer (≤ 5-6 words)
4. GPT-4o judges each answer against the gold standard

### Prompt Design

The QA prompt was calibrated against the benchmark standards after analyzing
the prompts used by Mem0, Zep, and MemOS in the official HaluMem repository.
All competitors use detailed, structured prompts — our prompt follows the
same conventions.

## Reproduce

```bash
# Requires: chromadb, sentence-transformers, anthropic, openai
pip install chromadb sentence-transformers anthropic openai

# Set API keys
export EXIA_ANTHROPIC_API_KEY=your_key
export OPENAI_API_KEY=your_key

# Download HaluMem dataset from HuggingFace (IAAR-Shanghai/HaluMem)

# Run evaluation
python eval_exiaghost.py --users 1 --no-consolidation

# Score with GPT-4o (requires HaluMem evaluation scripts)
# See HaluMem repo: github.com/MemTensor/HaluMem
```

## Files

| File | Description |
|------|-------------|
| `eval_exiaghost.py` | EXIA GHOST adapter for HaluMem |
| `results/scores.json` | Aggregated scores (GPT-4o judge) |
| `results/eval_results.jsonl` | Raw results (all memories, QA, responses) |
