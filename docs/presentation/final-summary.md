# Final Project Summary

## One-sentence project goal

Test whether youth slang normalization can be modeled as a shared low-dimensional direction in embedding space, which we call `Eigenslang`.

## Problem setup

- We map slang expressions to neutral paraphrases.
- We compare two formulations:
  - `term_paraphrase`: slang term vs. neutral expression
  - `contextual_sentence`: slang sentence vs. neutralized sentence
- We evaluate retrieval with:
  - `raw`
  - `mean offset`
  - `PCA Eigenslang`

## Main dataset

- Primary dataset: `96` curated examples
- Sources:
  - `60` manual examples
  - `36` cleaned examples from `MLBtrio/genz-slang-dataset`
- We also tested:
  - a Kaggle-derived augmentation
  - an abbreviation-filtered ablation

## Main quantitative result

On the primary 96-example dataset with sentence-transformers:

- `term_paraphrase + category_candidates`
  - raw: `Top-1 0.35`, `Top-3 0.65`
  - mean offset: `Top-1 0.35`, `Top-3 0.70`
  - PCA: `Top-1 0.35`, `Top-3 0.65`

- `term_paraphrase + balanced_distractors`
  - raw: `Top-1 0.40`, `Top-3 0.80`
  - mean offset: `Top-1 0.45`, `Top-3 0.75`
  - PCA: `Top-1 0.40`, `Top-3 0.80`

- `contextual_sentence + all_candidates`
  - raw: `Top-1 0.00`, `Top-3 0.05`
  - PCA: `Top-1 0.05`, `Top-3 0.10`

## Interpretation

- The proposal-faithful `term_paraphrase` setup performs best overall.
- PCA does **not** consistently improve over raw retrieval.
- The only small PCA gain appears in the harshest contextual all-candidate setting, and it disappears under fairer candidate sets.

## PCA result

- On the main dataset, PC1 explains only about `5%` of the variance.
- That is weak evidence for a dominant single global Eigenslang direction.

## Ablation result

When we removed abbreviation-like items from the merged dataset:

- raw retrieval improved a lot
- especially in the contextual formulation
- but PCA still did not become robustly helpful

Meaning:

- dataset heterogeneity matters
- acronym expansion and slang normalization are not exactly the same process
- but abbreviations were not the only reason the PCA hypothesis was weak

## Final conclusion

There is **weak, mixed evidence** for a shared slang direction, but not strong evidence for a single dominant global `Eigenslang` axis.

The strongest conclusion is:

- evaluation design matters
- dataset composition matters
- pretrained embeddings already capture some slang semantics
- a single PCA direction is too weak to serve as a reliable global normalization transform

## If asked “what did we learn?”

We learned that slang normalization has some structure, but it does not collapse cleanly into one universal linear direction.
The problem looks more category-dependent, context-dependent, and heterogeneous than the original hypothesis hoped.
