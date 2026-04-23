# Data Requirements and Expansion Plan

Date: 2026-04-23

## Current Diagnosis
The current dataset in `data/raw/slang_examples.csv` is useful for pipeline development, but it is not enough for final project-quality experiments.

Current state:

- 60 examples
- one slang expression per row
- one context sentence per row
- one neutral paraphrase per row
- category and notes metadata

This is enough to run the current pipeline, but not enough to make stable claims about whether an `Eigenslang` direction exists.

## Do We Already Have Neutral Data?
Yes, partially.

The current `neutral_paraphrase` column is the neutral target side of the normalization task. For example:

- `cooked` -> `in serious trouble`
- `mid` -> `mediocre`
- `rizz` -> `charisma`
- `no cap` -> `seriously`

So the dataset is not missing neutral labels entirely.

However, the neutral side is too minimal for the full project. We need richer neutral annotations.

## What Neutral Data Is Missing?
### 1. Canonical neutral term or phrase
The current `neutral_paraphrase` column often mixes different kinds of targets:

- single words: `mediocre`, `suspicious`, `okay`
- short phrases: `in serious trouble`, `very tasty`
- longer explanations: `received far more criticism than support`

For term-level offset experiments, we should add a cleaner field:

- `neutral_expression`

This should be the shortest neutral word or phrase that captures the meaning.

Example:

- slang term: `ratioed`
- current neutral paraphrase: `received far more criticism than support`
- possible neutral expression: `criticized heavily`

### 2. Explicit neutralized sentence
The current code creates a neutralized sentence automatically by replacing the slang expression with the neutral paraphrase. This is sometimes acceptable, but it can produce awkward or ungrammatical sentences.

We should add:

- `neutral_sentence`

Example:

- slang sentence: `He got ratioed after that rude reply.`
- automatic replacement: `He got received far more criticism than support after that rude reply.`
- better neutral sentence: `He received far more criticism than support after that rude reply.`

This field matters for the contextual sentence offset:

\[
\operatorname{Embed}(\text{slang sentence})
-
\operatorname{Embed}(\text{neutralized sentence})
\]

### 3. Paraphrase alternatives
Some slang expressions have multiple reasonable neutral translations.

Potential field:

- `neutral_alternatives`

Example:

- `fire`: `excellent; very good; impressive`

This can help with evaluation because a prediction may be semantically correct even if it does not exactly match the one annotated paraphrase.

### 4. Confidence or quality flag
Some examples are more reliable than others.

Potential field:

- `confidence`

Recommended values:

- `high`
- `medium`
- `low`

Only high- and medium-confidence examples should be used in final evaluation.

### 5. Source fields
We should track where examples came from.

Potential fields:

- `source_name`
- `source_url`
- `source_license_or_notes`

This matters if we use external datasets.

## Recommended Expanded Schema
The next cleaned dataset should use these columns:

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

Minimum required fields for final experiments:

- `id`
- `slang_term`
- `context_sentence`
- `neutral_expression`
- `neutral_paraphrase`
- `neutral_sentence`
- `category`
- `confidence`

## Why More Data Is Needed
The current 60-example dataset has two problems.

### 1. Statistical instability
With a 60/20/20 split, the test set has only about 12 examples. One correct or incorrect prediction changes the reported accuracy substantially.

### 2. Category imbalance
Several categories have only one or two examples. This makes per-category analysis weak and makes category-aware candidate sets less reliable.

Observed examples:

- `judgment`: 7 examples
- `intensifier`: 5 examples
- `online`: 5 examples
- many categories have only 1 example

For a stronger project, we should target 80 to 120 examples with more balanced categories.

## External Data Sources
### Hugging Face: `MLBtrio/genz-slang-dataset`
This looks useful as a candidate source for expansion.

Observed fields from the dataset page:

- `Slang`
- `Description`
- `Example`
- `Context`

The dataset page reports about 1.78k rows.

How we can use it:

- `Slang` -> `slang_term`
- `Description` -> candidate `neutral_paraphrase`
- `Example` -> `context_sentence`
- `Context` -> source notes or annotation aid

Important caveat:

- This dataset does not directly provide a manually written `neutral_sentence`, so we still need to generate or manually edit neutralized sentences.

### Kaggle: `genz-slang-pairs-1k`
This may be useful, but it appears closer to style-transfer data from neutral/formal text into Gen Z slang.

Potential use:

- secondary source only
- useful if it gives paired neutral/slang expressions

Caveat:

- It may not match our normalization task as well as the Hugging Face dataset.

## Recommended Data Expansion Strategy
### Step 1: Do not simply add rows blindly
Adding more noisy examples will not help. We need examples that support the exact evaluation.

### Step 2: Add explicit neutral fields
Before expanding to 100+ rows, update the schema to include:

- `neutral_expression`
- `neutral_sentence`
- `confidence`

### Step 3: Expand to 100 high-quality examples
Target category distribution:

- `judgment`: 10-15
- `intensifier`: 8-12
- `emotion`: 8-12
- `performance`: 8-12
- `online`: 8-12
- `dating_social`: 8-12
- `appearance_style`: 8-12
- `agreement_discourse`: 6-10
- `action_event`: 6-10

### Step 4: Keep two dataset files
Recommended files:

- `data/raw/slang_examples.csv`
- `data/processed/slang_examples_clean.csv`

The raw file can preserve source-derived examples. The processed file should contain cleaned annotations used for experiments.

## Final Recommendation
The user concern is correct:

- 60 examples is not enough for final claims.
- We need stronger neutral-side annotations.

The correction is:

- We are not missing neutral data entirely, because `neutral_paraphrase` already exists.
- We are missing a more structured neutral side: `neutral_expression`, `neutral_sentence`, and possibly `neutral_alternatives`.

The next implementation step should be to update the schema and create a cleaned processed dataset before adding many more examples.
