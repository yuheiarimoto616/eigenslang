# Qualitative Error Analysis

Date: 2026-04-24

Primary source files:

- `results/tables/no_abbrev/baseline_predictions_sentence_transformers_all_minilm_l6_v2_term_paraphrase_all_candidates.csv`
- `results/tables/no_abbrev/baseline_predictions_sentence_transformers_all_minilm_l6_v2_contextual_sentence_category_candidates.csv`
- `results/tables/no_abbrev/baseline_predictions_sentence_transformers_all_minilm_l6_v2_contextual_sentence_balanced_distractors.csv`

## Main pattern

On the abbreviation-filtered dataset, raw sentence-transformer retrieval is often already close to the correct neutral target.
PCA rarely fixes a large semantic error.
Instead, it usually does one of two things:

- slightly reorders semantically similar candidates
- replaces a correct or near-correct target with a generic positive or stylistically nearby label

This matches the aggregate metric story: the embedding space already contains meaningful slang semantics, but the learned PCA direction is too weak to function as a stable global correction.

## Representative examples

### Small local improvement

- `fire` in contextual sentence mode
- gold label: `excellent`
- raw top predictions: `suspicious || excellent || is excellent`
- PCA top predictions: `excellent || is excellent || suspicious`

Interpretation:

- PCA helps only by swapping the rank order of nearby candidates.
- This is a modest improvement, not evidence of a strong global transformation.

### Raw already works well

- `Normalize` in contextual sentence mode
- gold label: `Make something the norm.`
- raw top predictions: `Make something the norm. || show off || the center of attention`

Interpretation:

- The pretrained embedding space already captures the intended semantics fairly well.
- No learned direction is needed here.

### PCA hurts by demoting the correct target

- `hits different` in contextual sentence mode
- gold label: `feels especially good`
- raw top predictions: `feels especially good || excellent || suspicious`
- PCA top predictions: `excellent || feels especially good || is excellent`

Interpretation:

- PCA shifts the query toward a generic positive direction instead of the more specific intended meaning.

### PCA hurts by removing the correct answer from the top three

- `ick` in contextual balanced-distractor mode
- gold label: `a feeling of sudden disgust`
- raw top predictions: `Angry or frustrated. || harshly called out || a feeling of sudden disgust`
- PCA top predictions: `harshly called out || Cool or excellent. || charisma`

Interpretation:

- The learned direction is not only weak but can be actively misleading when slang items are semantically idiosyncratic.

## What the abbreviation ablation shows

Removing abbreviation-like items improved retrieval substantially, especially for contextual sentence evaluation.
This suggests that acronym expansion and slang normalization are not exactly the same phenomenon and should not automatically be modeled with one shared linear direction.

However, the PCA component still explains only a small fraction of total variance, so the main conclusion remains the same:

- dataset composition matters
- heterogeneity hurts
- but even the cleaner dataset does not reveal a strong universal Eigenslang axis
