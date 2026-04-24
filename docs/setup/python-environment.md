# Python Environment Setup

This project now includes a local virtual environment directory at `.venv/`.

## Current status

- The project was originally developed from the system Python environment.
- A project-local virtual environment has now been created at `.venv/`.
- `requirements.txt` is a full `pip freeze` from the original system environment.
- `requirements-project.txt` is the cleaner project-specific dependency list to use for reproduction.

## Recommended setup for a teammate

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-project.txt
```

## Verify the environment

```bash
which python
python -m pip list
python experiments/run_baseline.py --input data/processed/slang_examples_clean.csv --backend sentence-transformer --representation-mode term_paraphrase --candidate-mode category_candidates
```

## Notes

- The main experiment code depends on `numpy`, `pandas`, `scikit-learn`, `sentence-transformers`, `torch`, `transformers`, and `huggingface_hub`.
- `matplotlib` is included because the artifact-generation script uses it, even though figure export was flaky in this environment.
- Report compilation uses `tectonic`, which is separate from the Python environment.
