# Eigenslang Project Plan

Last updated: 2026-03-28

## Core decision
Keep the project narrowly scoped.

Primary project question:

Can a low-dimensional embedding-space transformation improve slang normalization over simple baselines?

Project identity:

- Keep `Eigenslang` as the project name.
- Treat `Eigenslang` as a testable hypothesis, not as a grand theory of slang.

## Main task
Use one primary task:

- `slang normalization`

Task definition:

- Given a slang expression in context, retrieve its intended neutral paraphrase from a candidate set.

Example:

- Input: `bro is cooked after that exam`
- Target: `in serious trouble` / `done for`

## Scope decisions
What to keep:

- one curated dataset
- one main embedding model
- simple baselines
- one PCA/SVD-based `Eigenslang` method
- one clean evaluation task

What to drop or keep secondary:

- slang generation
- broad claims like “help AI understand slang”
- large-scale scraping
- too many models
- ambitious claims about all Gen Z / Gen Alpha slang

## Dataset plan
Target size:

- about 80 to 120 examples

Each example should include:

- slang word or phrase
- full context sentence
- neutral paraphrase
- optional category label

Important annotation rule:

- annotate meanings in context, not isolated words

Reason:

- many slang expressions are polysemous, such as `cooked` or `ate`

## Methods to compare
Use these methods:

1. Raw embedding retrieval baseline
2. Mean offset baseline
3. `Eigenslang` method using PCA or SVD on slang-neutral difference vectors

Optional only if time remains:

- one second embedding model
- exploratory slang generation

## Evaluation plan
Main metrics:

- Top-1 accuracy
- Top-3 accuracy

Also include:

- a few success cases
- a few failure cases

Important comparison:

- show whether `Eigenslang` beats raw retrieval and mean-offset baselines

## Risk / fallback
Main risk:

- slang may be too heterogeneous for a single direction

If that happens:

- test whether a few components help
- analyze whether failure comes from context dependence or polysemy

Negative results are acceptable and still meaningful.

## One-month execution plan
Week 1:

- finalize task definition
- define annotation format
- collect and clean initial dataset
- implement raw retrieval baseline

Week 2:

- implement mean-offset baseline
- implement `Eigenslang` PCA/SVD method
- run first experiments

Week 3:

- perform error analysis
- optionally compare one additional embedding model
- prepare figures and tables

Week 4:

- polish experiments
- write report
- tighten claims and limitations

## Proposal decision
Proposal should emphasize:

- clear ML problem
- concrete evaluation task
- modest and realistic scope
- meaningful contribution even if results are negative
