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
- `evaluate.py` writes report-ready CSV tables.

First runnable experiment:

```bash
python3 experiments/run_baseline.py --input data/raw/slang_examples.csv
```

Semantic embedding experiment:

```bash
python3 experiments/run_baseline.py \
  --input data/raw/slang_examples.csv \
  --backend sentence-transformer \
  --model sentence-transformers/all-MiniLM-L6-v2
```
