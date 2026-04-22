# Data Layout

- `raw/`: manually collected candidate examples and source notes
- `processed/`: cleaned dataset files, splits, and task-ready artifacts

Recommended first file:

- `raw/slang_examples.csv`

Recommended columns:

- `id`
- `slang_term`
- `context_sentence`
- `neutral_paraphrase`
- `category`
- `source_type`
- `notes`

Current schema notes:

- `id`, `slang_term`, `context_sentence`, and `neutral_paraphrase` are required and must be non-empty.
- `category`, `source_type`, and `notes` may be empty, but the columns must exist so the data loader stays stable.

Minimal workflow:

1. Add manually curated examples to `raw/slang_examples.csv`.
2. Run `python3 experiments/run_baseline.py`.
3. Inspect generated splits in `data/splits/`.
4. Inspect metrics and predictions in `results/tables/`.
