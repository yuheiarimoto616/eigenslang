# Source Layout

Suggested modules:

- `dataset.py`: loading, validation, splitting
- `embeddings.py`: embedding model wrappers
- `baselines.py`: raw retrieval and mean-offset methods
- `eigenslang.py`: PCA or SVD training and inference
- `evaluate.py`: metrics and report-friendly summaries

Current implementation:

- `dataset.py` validates the CSV schema and creates deterministic train, validation, and test splits.
- `embeddings.py` provides pluggable embedding backends for TF-IDF and sentence-transformer models.
- `baselines.py` provides raw retrieval, mean-offset, and PCA-based `Eigenslang` on top of a shared embedding interface.
- `baselines.py` supports two representation modes:
  - `contextual_sentence`: `Embed(slang sentence) - Embed(neutral sentence)`
  - `term_paraphrase`: `Embed(slang term) - Embed(neutral expression)`
- `evaluate.py` writes report-ready CSV tables.

TF-IDF sanity checks:

```bash
python3 experiments/run_baseline.py \
  --input data/processed/slang_examples_clean.csv \
  --backend tfidf \
  --representation-mode contextual_sentence

python3 experiments/run_baseline.py \
  --input data/processed/slang_examples_clean.csv \
  --backend tfidf \
  --representation-mode term_paraphrase
```

Semantic embedding experiment:

```bash
python3 experiments/run_baseline.py \
  --input data/processed/slang_examples_clean.csv \
  --backend sentence-transformer \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --representation-mode contextual_sentence

python3 experiments/run_baseline.py \
  --input data/processed/slang_examples_clean.csv \
  --backend sentence-transformer \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --representation-mode term_paraphrase
```
