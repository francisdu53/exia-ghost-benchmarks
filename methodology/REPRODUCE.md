# How to Reproduce — EXIA GHOST Benchmarks

## Prerequisites

```bash
# Python 3.12+
python3 --version

# Install dependencies
pip install chromadb sentence-transformers anthropic openai spacy tqdm
python3 -m spacy download fr_core_news_sm
```

## API Keys

Two API keys are required for full benchmark evaluation:

```bash
# Claude Haiku (memory extraction + QA generation)
export EXIA_ANTHROPIC_API_KEY=your_anthropic_key

# GPT-4o / GPT-4o-mini (benchmark judge)
export OPENAI_API_KEY=your_openai_key
```

## LoCoMo Benchmark

### 1. Download the dataset

```bash
git clone https://github.com/snap-research/locomo.git
# Dataset: locomo/data/locomo10.json
```

### 2. Run the evaluation

```bash
cd locomo/
python eval_locomo.py --convs 10
```

Options:
- `--convs N` : evaluate first N conversations (1-10)
- `--dry` : dry run without API calls (test pipeline only)

### 3. Results

Results are saved to `results/exiaghost-v5/locomo_eval_results.json`

### Expected cost

- Claude Haiku (extraction + QA): ~$0.50
- GPT-4o-mini (judge): ~$0.65
- **Total: ~$1.15**
- Duration: ~90 minutes on 2 vCPU

## HaluMem Benchmark

### 1. Download the dataset

```bash
# From HuggingFace
pip install huggingface_hub
python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download('IAAR-Shanghai/HaluMem', 'HaluMem-Medium.jsonl',
                repo_type='dataset', local_dir='data')
"
```

### 2. Run the evaluation

```bash
cd halumem/
python eval_exiaghost.py --users 1 --no-consolidation
```

Options:
- `--users N` : evaluate first N users (1-20)
- `--dry` : dry run without API calls
- `--no-consolidation` : disable batch consolidation (recommended for benchmark)

### 3. Score with GPT-4o judge

Requires the HaluMem evaluation scripts:

```bash
git clone https://github.com/MemTensor/HaluMem.git
cd HaluMem/eval/

# Configure .env
echo "OPENAI_API_KEY=your_key" > .env
echo "OPENAI_MODEL=gpt-4o" >> .env
echo "RETRY_TIMES=10" >> .env
echo "WAIT_TIME_LOWER=15" >> .env
echo "WAIT_TIME_UPPER=60" >> .env

# Run evaluation
python evaluation.py --frame exiaghost --version v5
```

### Expected cost

- Claude Haiku (extraction + QA): ~$0.40
- GPT-4o (judge): ~$8-10
- **Total: ~$10 per user**
- Duration: ~4 hours on 2 vCPU (rate-limited by GPT-4o Tier 1)

## Notes

- All benchmarks start with **clean memory** (temporary ChromaDB, deleted after run)
- No pre-loaded data, no fine-tuning, no dataset-specific optimization
- The same EXIA GHOST code runs for all benchmarks — only the adapter changes
- Results may vary slightly between runs due to LLM non-determinism
  (temperature is set to 0.0, but minor variations can occur)
