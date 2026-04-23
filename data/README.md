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

Planned final schema:

- `id`
- `slang_term`
- `context_sentence`
- `neutral_expression`
- `neutral_paraphrase`
- `neutral_sentence`
- `neutral_alternatives`
- `category`
- `source_type`
- `source_name`
- `source_url`
- `confidence`
- `notes`

Rationale:

- `neutral_paraphrase` is already the neutral target label, so the current dataset does have neutral-side data.
- `neutral_expression` is needed for proposal-faithful term/paraphrase offset experiments.
- `neutral_sentence` is needed for cleaner contextual sentence offset experiments because automatic replacement can produce ungrammatical neutralized sentences.
- `neutral_alternatives` can help track other acceptable normalizations.
- `confidence` allows low-quality or uncertain examples to be excluded from final evaluation.

Minimal workflow:

1. Add manually curated examples to `raw/slang_examples.csv`.
2. Run `python3 experiments/run_baseline.py`.
3. Inspect generated splits in `data/splits/`.
4. Inspect metrics and predictions in `results/tables/`.

External dataset workflow:

1. Download the Hugging Face source dataset:

```bash
python3 scripts/import_hf_genz_dataset.py
```

2. Clean and map it into the Eigenslang schema:

```bash
python3 scripts/clean_external_genz_dataset.py
```

3. Review the candidate output:

```text
data/processed/slang_examples_candidate_external.csv
```

4. Build a first clean experiment dataset:

```bash
python3 scripts/build_clean_dataset.py
```

This writes:

- `data/processed/slang_examples_clean.csv`
- `data/processed/slang_examples_clean_rejected.csv`
- `data/processed/slang_examples_clean_report.txt`

Important:

- External data should be treated as a candidate pool, not automatically trusted final data.
- Cite `MLBtrio/genz-slang-dataset` in the final report if any imported rows are used.


I found a couple interesting datasets:
https://www.kaggle.com/datasets/programmerrdai/genz-slang-pairs-1k

But it seems like a strict rewrite from neutral/formal tone to Gen Z slang (seems to be used for style transfer)

This one seems a lot better:
https://huggingface.co/datasets/MLBtrio/genz-slang-dataset

Some talk about the eigenslur:
https://www.reddit.com/r/LocalLLaMA/comments/1pp5otm/help_me_prove_eigenslur_hypothesis_built_within/#:~:text=We%20can%20go%20further%2C%20by,have%20constructed%20a%20candidate%20eigenslur.
