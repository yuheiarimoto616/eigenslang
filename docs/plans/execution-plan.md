# Eigenslang Execution Plan

Last updated: 2026-04-20

## Goal
Complete the CPSC 440 course project proposed in `project-proposal.tex` as a focused empirical study:

**Can a low-dimensional direction in embedding space help normalize youth slang into neutral paraphrases?**

The final output should satisfy the report expectations in `project-format/project.tex`:

- a clear problem statement and motivation
- related work discussion
- description and justification of methods
- experiments and analysis
- discussion of strengths, weaknesses, and future work

## Project Scope
This project should stay narrow and testable.

In scope:

- a manually curated slang dataset
- one main task: slang normalization in context
- one primary embedding family for the main result
- simple baselines
- one main `Eigenslang` method using PCA or SVD
- quantitative evaluation plus qualitative error analysis
- a six-page conference-style report

Out of scope unless the main pipeline is already working:

- large-scale scraping
- training a new language model
- broad claims about all Gen Z or Gen Alpha language
- full chatbot integration
- slang generation as a primary contribution

## Research Question and Success Criteria
Primary question:

- Does a shared low-dimensional slang-to-neutral offset exist strongly enough to improve retrieval-based normalization?

Minimum success criteria for a solid course project:

- build a clean dataset of roughly 80 to 120 curated examples
- implement at least two baselines and one `Eigenslang` method
- report Top-1 and Top-3 retrieval accuracy on a held-out set
- include at least one figure and one compact summary table
- provide error analysis and limitations

The project is still acceptable if the answer is "no", provided the experiments are careful and the negative result is analyzed properly.

## Dataset Plan
### Unit of annotation
Each example should represent a meaning in context, not just a slang token in isolation.

Each row should include:

- `id`
- `slang_term`
- `context_sentence`
- `neutral_paraphrase`
- `category` (optional but useful)
- `notes` (optional annotation rationale)
- `source_type` such as dictionary, trend list, or social media-derived paraphrase

### Dataset size

- target: 80 to 120 examples
- initial milestone: first 30 high-confidence examples
- preferred split after full collection:
  - train: about 60%
  - validation: about 20%
  - test: about 20%

### Annotation rules

- paraphrase the intended meaning in the given sentence
- prefer short neutral phrases over long explanations
- avoid examples whose meaning cannot be inferred reliably
- avoid near-duplicate contexts
- record polysemous terms in multiple rows if meanings differ by context

### Dataset risks

- many slang terms are context dependent
- some terms become mainstream quickly and lose their "slang-only" character
- some examples may need sentence-level rather than word-level embeddings

## Experimental Plan
### Task definition
Given a slang expression in context, retrieve the correct neutral paraphrase from a candidate set.

### Candidate methods
Baselines:

1. Raw retrieval using original embeddings
2. Mean offset baseline from average slang-neutral difference vectors

Main method:

3. `Eigenslang` using PCA or SVD over slang-neutral difference vectors

Optional extension after the main result is stable:

4. Multi-component variant using top-k principal components
5. Comparison against a second embedding model

### Recommended modeling order
Start with the simplest pipeline that can produce end-to-end numbers:

1. sentence embedding for context sentence
2. embedding for neutral paraphrase candidates
3. retrieval by cosine similarity
4. mean-offset correction
5. PCA/SVD correction

This reduces the risk of getting stuck on token-level edge cases too early.

### Hyperparameters to tune

- embedding model choice
- whether to embed the full context sentence or a templated sentence
- number of principal components
- scaling factor `alpha`
- candidate set construction for evaluation

## Evaluation Plan
Primary metrics:

- Top-1 retrieval accuracy
- Top-3 retrieval accuracy

Supporting analysis:

- qualitative examples of correct normalization
- failure cases grouped by error type
- inspection of nearest neighbors before and after applying the direction

Recommended figures/tables:

- figure: variance explained by the top principal components
- figure: 2D projection or example movement in embedding space
- table: Top-1 and Top-3 accuracy across methods
- table or appendix: representative successes and failures

## Report Plan
Target paper structure aligned with the course format:

1. Introduction
2. Related Work
3. Dataset and Task Setup
4. Methods
5. Experiments
6. Discussion and Limitations
7. Conclusion

Each section should explicitly answer the grading expectations from `project-format/project.tex`.

## Work Plan
### Phase 1: Foundation

- finalize dataset schema
- create example collection sheet
- gather 30 high-confidence examples
- define the held-out evaluation setup

### Phase 2: Baselines

- implement raw retrieval baseline
- implement mean-offset baseline
- verify the evaluation script on a small subset

### Phase 3: Main Method

- compute slang-neutral difference vectors
- run PCA or SVD on training examples only
- tune the scaling factor on validation data
- evaluate on held-out test data

### Phase 4: Analysis

- inspect whether the top component is interpretable
- group errors by category
- decide whether adding more components helps

### Phase 5: Writing

- convert notes and results into the final report
- keep claims modest and evidence-backed
- emphasize either the improvement or the negative finding

## Deliverables to Produce in This Repository
- `data/raw/` for initial manually collected examples
- `data/processed/` for cleaned dataset files and splits
- `src/` for reusable code
- `experiments/` for run scripts or notebooks
- `results/figures/` and `results/tables/` for report assets
- `report/` for the final paper source and outline
- `docs/decisions/` for scope and methodology decisions

## Recommended Immediate Next Steps
1. Create a first dataset file with 20 to 30 manually curated examples.
2. Decide the initial embedding model and evaluation protocol.
3. Implement a minimal end-to-end baseline before collecting the full dataset.
4. Only after the baseline works, expand the dataset and run the main method.
