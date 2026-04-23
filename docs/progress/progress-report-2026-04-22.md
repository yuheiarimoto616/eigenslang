# Eigenslang Progress Report

Date: 2026-04-22

## Summary
This report documents the implementation work completed after the initial project planning phase, along with the current experimental results.

The project is no longer just a proposal and plan. It now has:

- a defined dataset schema
- a seed dataset with starter examples
- deterministic train, validation, and test splitting
- a runnable retrieval experiment pipeline
- three methods implemented:
  - raw retrieval
  - mean-offset baseline
  - PCA-based `Eigenslang`
- two embedding backends implemented:
  - TF-IDF
  - sentence-transformer (`all-MiniLM-L6-v2`)

## What Was Implemented
### 1. Repository structure
The repository was organized so that data, experiments, report assets, and planning documents are separated cleanly.

Relevant directories:

- `docs/plans/`
- `docs/decisions/`
- `data/raw/`
- `data/processed/`
- `data/splits/`
- `src/`
- `experiments/`
- `results/figures/`
- `results/tables/`
- `report/`

### 2. Planning and decision documents
The following documents were created earlier and remain current:

- `docs/plans/execution-plan.md`
- `docs/decisions/decision-log.md`
- `report/outline.md`

These documents define the project scope, the main task, evaluation strategy, and the reasoning for keeping the project narrow and empirical.

### 3. Dataset schema and validation
Implemented in `src/dataset.py`.

Current required columns:

- `id`
- `slang_term`
- `context_sentence`
- `neutral_paraphrase`
- `category`
- `source_type`
- `notes`

Current dataset features:

- CSV loading and validation
- duplicate id detection
- empty required-field detection
- deterministic train, validation, and test splits
- split export to `data/splits/`

### 4. Seed dataset
Created and populated:

- `data/raw/slang_examples.csv`

Current size:

- 60 examples total
- 20 initial seed examples
- 40 additional manually curated examples

The dataset is now large enough for a first non-toy experiment, but it is still too small for strong conclusions.

### 5. Retrieval and evaluation pipeline
Implemented in:

- `src/baselines.py`
- `src/evaluate.py`
- `experiments/run_baseline.py`

The current experiment pipeline does the following:

1. loads the raw CSV
2. validates the schema
3. creates train, validation, and test splits
4. embeds examples
5. runs:
   - raw retrieval
   - mean-offset retrieval
   - PCA-based `Eigenslang`
6. tunes `alpha` on validation data where relevant
7. writes metrics and prediction tables to `results/tables/`

### 6. Embedding backends
Implemented in `src/embeddings.py`.

Current backends:

- `tfidf`
- `sentence-transformer`

Installed package:

- `sentence-transformers`

Downloaded and cached model:

- `sentence-transformers/all-MiniLM-L6-v2`

Important implementation note:

- sentence-transformer loading was configured to use local cached files by default after the first download, so future runs work offline inside the sandbox.

## Issues Found and Fixed
### 1. Python package import issue
Initial baseline execution failed because `src` was not importable from the experiment script.

Fix:

- added `src/__init__.py`
- inserted project root into `sys.path` in `experiments/run_baseline.py`

### 2. CSV formatting bug
The first seed CSV contained commas in text fields without proper quoting, which caused incorrect parsing.

Fix:

- rewrote `data/raw/slang_examples.csv` with proper CSV quoting

### 3. Weak candidate representation in the first baseline
The earliest retrieval version compared full slang contexts against bare paraphrase strings, which was too weak and mismatched the intended task.

Fix:

- candidate paraphrases are now scored inside the original sentence context by replacing the slang term with the candidate paraphrase when possible

### 4. Results overwriting
Earlier runs wrote generic files such as `baseline_metrics.csv`, which meant one backend run could overwrite another.

Fix:

- backend-specific result filenames are now generated automatically

## Current Results
The project now has two distinct result stages:

- an initial 20-example seed run used mainly for pipeline verification
- a later 60-example run used as the first more realistic experiment

The 20-example results remain useful as a sanity check. The 60-example results are more relevant going forward.

### TF-IDF results
Source:

- `results/tables/baseline_metrics_tfidf.csv`

Metrics:

| Split | Method | Top-1 | Top-3 | Alpha |
| --- | --- | ---: | ---: | ---: |
| train | raw | 0.0833 | 0.25 | |
| train | mean_offset | 0.0833 | 0.25 | 0.0 |
| train | eigenslang_pca | 0.0833 | 0.25 | 0.0 |
| validation | raw | 0.0000 | 0.00 | |
| validation | mean_offset | 0.0000 | 0.00 | 0.0 |
| validation | eigenslang_pca | 0.0000 | 0.00 | 0.0 |
| test | raw | 0.0000 | 0.25 | |
| test | mean_offset | 0.0000 | 0.25 | 0.0 |
| test | eigenslang_pca | 0.0000 | 0.25 | 0.0 |

Interpretation:

- TF-IDF is useful as a lexical baseline and for verifying that the pipeline runs.
- It does not capture enough semantic information for this task.

### Sentence-transformer results
Source:

- `results/tables/baseline_metrics_sentence_transformers_all_minilm_l6_v2.csv`

Metrics:

| Split | Method | Top-1 | Top-3 | Alpha |
| --- | --- | ---: | ---: | ---: |
| train | raw | 0.1667 | 0.25 | |
| train | mean_offset | 0.1667 | 0.25 | 0.0 |
| train | eigenslang_pca | 0.0833 | 0.25 | 0.5 |
| validation | raw | 0.0000 | 0.25 | |
| validation | mean_offset | 0.0000 | 0.25 | 0.0 |
| validation | eigenslang_pca | 0.2500 | 0.50 | 0.5 |
| test | raw | 0.0000 | 0.00 | |
| test | mean_offset | 0.0000 | 0.00 | 0.0 |
| test | eigenslang_pca | 0.0000 | 0.00 | 0.5 |

Interpretation:

- The sentence-transformer backend is slightly stronger than TF-IDF on the starter dataset.
- The PCA-based `Eigenslang` direction showed a small validation improvement, but there is no meaningful test-set evidence yet.
- The dataset is too small for stable conclusions about whether the `Eigenslang` hypothesis works.

### Updated sentence-transformer results after dataset expansion
Source:

- `results/tables/baseline_metrics_sentence_transformers_all_minilm_l6_v2.csv`

Dataset size at run time:

- 60 examples

Metrics:

| Split | Method | Top-1 | Top-3 | Alpha |
| --- | --- | ---: | ---: | ---: |
| train | raw | 0.0278 | 0.2222 | |
| train | mean_offset | 0.0278 | 0.2222 | 0.0 |
| train | eigenslang_pca | 0.1111 | 0.1667 | 0.25 |
| validation | raw | 0.0000 | 0.0833 | |
| validation | mean_offset | 0.0000 | 0.0833 | 0.0 |
| validation | eigenslang_pca | 0.0833 | 0.25 | 0.25 |
| test | raw | 0.0000 | 0.0833 | |
| test | mean_offset | 0.0000 | 0.0833 | 0.0 |
| test | eigenslang_pca | 0.0000 | 0.0000 | 0.25 |

Interpretation:

- The larger dataset makes the task meaningfully harder.
- The raw semantic baseline remains weak.
- The PCA-based `Eigenslang` method again shows a small validation gain, but still no convincing held-out test improvement.
- This strengthens the case that the next bottleneck is task formulation and data quality, not just adding another model.

## What These Results Mean Right Now
The current experiments support the following claims:

- the project infrastructure is functioning end to end
- the retrieval task is operational
- the project can compare lexical and semantic embeddings
- the code can train and evaluate both a mean-offset baseline and a PCA-based `Eigenslang` method
- the dataset has moved beyond a pure toy example and can now expose genuine failure modes

The current experiments do **not** support the following claims yet:

- that `Eigenslang` improves normalization in a reliable way
- that sentence-transformer embeddings solve the task well
- that the current results generalize beyond the small seed dataset

## Files Added or Updated During Implementation
Main code files:

- `src/__init__.py`
- `src/dataset.py`
- `src/baselines.py`
- `src/embeddings.py`
- `src/evaluate.py`
- `scripts/import_hf_genz_dataset.py`
- `scripts/clean_external_genz_dataset.py`
- `experiments/run_baseline.py`

Data and documentation:

- `data/raw/slang_examples.csv`
- `data/README.md`
- `src/README.md`

Generated outputs:

- `data/splits/train.csv`
- `data/splits/validation.csv`
- `data/splits/test.csv`
- `data/raw/external/mlbtrio_genz_slang_dataset.csv`
- `data/processed/slang_examples_candidate_external.csv`
- `results/tables/baseline_metrics_tfidf.csv`
- `results/tables/baseline_predictions_tfidf.csv`
- `results/tables/baseline_metrics_sentence_transformers_all_minilm_l6_v2.csv`
- `results/tables/baseline_predictions_sentence_transformers_all_minilm_l6_v2.csv`

Note:

- older generic files like `baseline_metrics.csv` and `baseline_predictions.csv` remain from earlier runs and should not be treated as the current canonical outputs.

## External Dataset Import
An external candidate dataset was imported from Hugging Face:

- source: `MLBtrio/genz-slang-dataset`
- URL: `https://huggingface.co/datasets/MLBtrio/genz-slang-dataset`
- raw imported file: `data/raw/external/mlbtrio_genz_slang_dataset.csv`
- cleaned candidate file: `data/processed/slang_examples_candidate_external.csv`

The raw external dataset contains 1779 rows with columns:

- `Slang`
- `Description`
- `Example`
- `Context`

The cleaning script maps these into the richer Eigenslang schema and writes 300 candidate rows by default.

Important caveat:

- The cleaned external file is a candidate review pool, not final experiment data.
- Automatic neutral sentence generation can still produce awkward outputs.
- External rows should be manually reviewed or filtered before inclusion in final experiments.
- The source must be cited in the final report if any imported rows are used.

## Clean Dataset Build
A curation script now merges the manual dataset with selected external candidates:

- script: `scripts/build_clean_dataset.py`
- clean output: `data/processed/slang_examples_clean.csv`
- rejected output: `data/processed/slang_examples_clean_rejected.csv`
- build report: `data/processed/slang_examples_clean_report.txt`

Current clean dataset:

- 96 rows total
- 60 manual rows
- 36 selected external rows
- 264 external rows rejected or skipped by filters

Current review status:

- 52 manual rows accepted directly
- 8 manual rows flagged for neutral sentence review
- 36 external rows selected automatically

Important caveat:

- `slang_examples_clean.csv` is a stronger experiment dataset than the raw file, but it still needs a small manual pass over rows flagged as `manual_seed_neutral_sentence_review`.
- The selected external rows should also be spot-checked before final report experiments.

## Representation Mode Experiments
The baseline pipeline now supports two offset formulations:

- `contextual_sentence`: `Embed(slang sentence) - Embed(neutral sentence)`
- `term_paraphrase`: `Embed(slang term) - Embed(neutral expression)`

This addresses the methodological difference between the original proposal and the first implementation.

Current result files include:

- `results/tables/baseline_metrics_tfidf_contextual_sentence.csv`
- `results/tables/baseline_metrics_tfidf_term_paraphrase.csv`
- `results/tables/baseline_metrics_sentence_transformers_all_minilm_l6_v2_contextual_sentence.csv`
- `results/tables/baseline_metrics_sentence_transformers_all_minilm_l6_v2_term_paraphrase.csv`

Current high-level result on `data/processed/slang_examples_clean.csv`:

- Contextual sentence mode with sentence-transformer: PCA `Eigenslang` improves test Top-1 from 0.0000 to 0.0500 and test Top-3 from 0.0500 to 0.1000.
- Term/paraphrase mode with sentence-transformer: raw, mean-offset, and PCA all have the same test Top-1 of 0.1000 and Top-3 of 0.2500.
- TF-IDF remains a weak lexical baseline.

Interpretation:

- The proposal-faithful term/paraphrase formulation now exists and can be reported honestly.
- The contextual sentence formulation shows a small PCA gain on the current split, but the absolute numbers are still low.
- The next likely bottleneck is candidate-set difficulty and analysis tooling, not just embedding choice.

## Recommended Next Step
The next highest-value step is dataset expansion, not more model work.

Recommended immediate action:

- improve the task setup and candidate construction now that the dataset has reached 60 examples

Reason:

- the dataset is no longer the only blocker
- the current retrieval setup is still very challenging and may be obscuring any real offset structure
- the project now needs better evaluation design in addition to continued dataset refinement
