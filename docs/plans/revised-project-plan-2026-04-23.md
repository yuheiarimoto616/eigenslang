# Revised Eigenslang Project Plan

Date: 2026-04-23

## Current Project State
The project now has enough infrastructure to support a serious course project:

- 60 curated slang-context-paraphrase examples
- deterministic train, validation, and test splits
- a runnable retrieval experiment
- TF-IDF baseline
- sentence-transformer backend using `sentence-transformers/all-MiniLM-L6-v2`
- raw retrieval baseline
- mean-offset baseline
- PCA-based `Eigenslang`
- metrics and prediction tables

The main current result is not that the method works. The main result is that the initial all-candidate retrieval task is very hard and may be too blunt to reveal whether a slang direction exists.

## Updated Goal
The goal should be to produce a strong CPSC 440 project by making the experiment rigorous and interpretable, not by forcing a positive result.

Final report thesis:

> We test whether slang-to-neutral normalization can be represented as a low-dimensional direction in embedding space, and analyze when this geometric hypothesis succeeds or fails.

This supports a good project even if the main result is negative, because the contribution is the controlled empirical test and error analysis.

## Critical Evaluation of Word2Vec
The teammate suggestion to use word2vec is reasonable, but it should not become the main method without evidence.

### Why word2vec is relevant
Word2Vec is directly aligned with the original geometric framing:

- it gives explicit word vectors
- vector offsets are a familiar use case
- PCA or SVD over difference vectors is conceptually clean
- it may be easier to explain in the report than sentence-transformer internals

For example, the project question can be expressed naturally as:

`slang_word_vector - neutral_word_vector = slang_offset`

This makes word2vec useful as a conceptual baseline or ablation.

### Why word2vec may be weak for this project
Word2Vec has several risks for this specific task:

- It is static, so it does not represent context-dependent meanings well.
- Many slang terms are recent, rare, phrase-level, or out of vocabulary.
- Terms like `ate`, `cooked`, `serve`, and `cap` have standard meanings, so static vectors may mostly encode the non-slang sense.
- Phrase-level examples like `let him cook`, `stood on business`, `touch grass`, and `hits different` are awkward under word-level averaging.
- Pretrained word2vec files are large and may add setup burden without improving the final result.

### Decision
Do not replace the current sentence-transformer backend with word2vec as the primary model.

Use word2vec only if it satisfies one of these conditions:

- it can be implemented quickly as a clean baseline
- pretrained vectors are already available locally or can be obtained without derailing the project
- it helps answer a specific report question, such as whether static word-level geometry is worse than context-aware sentence geometry

If we add it, frame it as:

> a static word-vector baseline for testing whether the Eigenslang hypothesis depends on contextual embeddings.

If it performs poorly, that is still useful: it supports the argument that modern slang normalization needs contextual or phrase-level representations.

### Better alternative if we want a word-level model
If we want a word-level embedding comparison, fastText is probably more appropriate than word2vec because fastText uses subword information and handles rare or novel forms better.

However, fastText is still secondary to fixing evaluation design.

## Updated Technical Plan
### Priority 1: Improve evaluation design
The current all-candidate retrieval task asks each example to retrieve its correct paraphrase from every paraphrase in the dataset. This is useful as a stress test, but it may be too noisy.

Add at least two evaluation settings:

1. `all_candidates`
   - correct paraphrase among all dataset paraphrases
   - hardest setting
   - keep for transparency

2. `category_candidates`
   - correct paraphrase plus candidates from the same broad category
   - tests finer-grained semantic distinction
   - avoids comparing unrelated meanings like food slang against dating slang

3. `balanced_distractors`
   - correct paraphrase plus a fixed number of distractors
   - include some same-category and some random distractors
   - report Top-1 and Top-3

This is the highest-value next implementation step.

### Priority 1.5: Compare offset formulations
The proposal describes a direct slang-expression minus neutral-paraphrase offset:

`Embed(slang term) - Embed(neutral paraphrase)`

The current implementation uses a context-preserving sentence offset:

`Embed(slang sentence) - Embed(neutralized sentence)`

Before final experiments, implement both modes and compare them explicitly. This is important because the sentence-level formulation is better motivated for polysemy and phrase-level slang, but the term/paraphrase formulation is closer to the original proposal.

### Priority 2: Expand and clean the dataset
Target dataset size:

- minimum: 80 examples
- preferred: 100 examples
- stretch: 120 examples

Dataset quality goals:

- reduce duplicate paraphrase styles
- keep paraphrases short and consistent
- ensure categories are useful for evaluation
- include multiple examples of key categories:
  - intensifier
  - emotion
  - judgment
  - performance
  - online/social media
  - dating/social interaction
  - appearance/style

### Priority 3: Add analysis outputs
The report needs more than accuracy numbers.

Add scripts or outputs for:

- variance explained by PCA components
- top successes and failures
- failure categories
- per-category accuracy
- examples where PCA helps or hurts

These will directly support the final report.

### Priority 4: Optional embedding comparison
After evaluation is improved, compare:

- TF-IDF
- sentence-transformer
- optional word2vec or fastText

Decision rule:

- Add word2vec only after the evaluation modes are implemented.
- Keep it only if implementation cost is low or it provides useful contrast.
- Do not spend substantial project time chasing word2vec performance.

## Recommended Method Stack for Final Report
The final project should compare the following methods:

1. Raw retrieval baseline
2. Mean-offset baseline
3. PCA `Eigenslang` with one component
4. Optional PCA `Eigenslang` with multiple components
5. Optional static word-vector baseline, if feasible

The report should emphasize:

- whether PCA helps over raw retrieval
- whether the effect is stable across evaluation settings
- what kinds of slang break the geometric assumption

## Report Strategy for a Good Grade
The project should be written as a careful empirical study.

Strong-grade priorities:

- clear motivation in the introduction
- precise task definition
- honest baselines
- controlled evaluation settings
- readable figures and tables
- strong error analysis
- modest claims

Avoid:

- claiming to solve slang normalization broadly
- over-indexing on one small accuracy number
- adding many models without explaining what each model tests
- relying on word2vec just because vector arithmetic is aesthetically aligned with the project name

## Updated Timeline
### Step 1: Evaluation redesign

- implement `all_candidates`, `category_candidates`, and `balanced_distractors`
- rerun TF-IDF and sentence-transformer experiments
- compare whether PCA helps under easier and harder candidate sets

### Step 2: Offset formulation comparison

- add a proposal-faithful `term_paraphrase` representation mode
- keep the current `contextual_sentence` representation mode
- compare both modes under the same candidate-set settings

### Step 3: Dataset expansion

- grow from 60 to 80-100 examples
- rebalance categories
- check paraphrase consistency

### Step 4: Analysis tooling

- generate per-category metrics
- generate PCA variance explained table or figure
- generate success and failure examples

### Step 5: Optional word2vec check

- inspect availability and setup cost
- implement only if it is quick
- report it as a static-vector baseline, not the main method

### Step 6: Final report

- write using `report/outline.md`
- use the best-controlled experiment as the main result
- discuss negative results clearly if PCA does not improve test accuracy

## Immediate Next Action
Implement the improved candidate-set evaluation.

Reason:

- It directly addresses the weakness exposed by the 60-example result.
- It gives more interpretable numbers.
- It will make any later word2vec comparison fairer and more useful.
