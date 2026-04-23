# Embedding Offset Formulation

Date: 2026-04-23

## Proposal Formulation
The project proposal describes the core `Eigenslang` idea as:

\[
\mathbf{d}_i = \mathbf{s}_i - \mathbf{n}_i,
\]

where:

- \(\mathbf{s}_i\) is the embedding of a slang expression
- \(\mathbf{n}_i\) is the embedding of its neutral paraphrase

The most direct interpretation is:

\[
\mathbf{d}_i =
\operatorname{Embed}(\text{slang term})
-
\operatorname{Embed}(\text{neutral paraphrase})
\]

This is the proposal-faithful term/paraphrase offset.

## Current Implementation
The current implementation computes an offset, but with a context-preserving sentence formulation:

\[
\mathbf{d}_i =
\operatorname{Embed}(\text{slang sentence})
-
\operatorname{Embed}(\text{neutralized sentence})
\]

In code:

- `build_query_text(row)` returns the full context sentence.
- `build_candidate_text(...)` replaces the slang term with a candidate neutral paraphrase inside that same context.
- `compute_mean_offset(...)` and `compute_eigenslang_direction(...)` compute differences using `query_matrix - target_matrix`.

This means the project is currently testing whether the *sentence-level transformation* from slang usage to neutralized usage has a shared direction.

## Why This Divergence Was Intentional
The context-preserving formulation was chosen because many examples in the dataset are context-dependent or phrase-level.

Examples:

- `ate` can mean consumed food or performed very well.
- `cooked` can mean prepared food or in serious trouble.
- `cap` can mean a hat or a lie.
- `serve` can mean provide service or perform stylishly.
- `let him cook`, `touch grass`, `stood on business`, and `hits different` are phrase-level expressions.

For these cases, an isolated word embedding may primarily encode the standard meaning rather than the intended slang meaning. A full-sentence embedding is more likely to preserve the annotated meaning in context.

## Methodological Decision
The current sentence-level formulation should not be presented as identical to the original proposal formulation.

Instead, the final project should explicitly distinguish two variants:

1. **Term/paraphrase offset**

   \[
   \operatorname{Embed}(\text{slang term})
   -
   \operatorname{Embed}(\text{neutral paraphrase})
   \]

   This is closest to the proposal and to traditional word-vector offset experiments.

2. **Contextual sentence offset**

   \[
   \operatorname{Embed}(\text{slang sentence})
   -
   \operatorname{Embed}(\text{neutralized sentence})
   \]

   This is the current implementation and is better motivated for polysemous and phrase-level slang.

## Recommendation for Final Report
The report should say something like:

> The proposal described \(d_i = s_i - n_i\), where \(s_i\) is a slang embedding and \(n_i\) is a neutral paraphrase embedding. In implementation, we evaluate two versions of this idea. The first uses direct term/paraphrase embeddings, matching the proposal closely. The second uses context-preserving sentence embeddings, where the slang sentence is compared to the same sentence with the slang expression replaced by its neutral paraphrase. We include the contextual variant because many slang terms are polysemous or phrase-level, so isolated word vectors may not represent the intended meaning.

## Next Implementation Implication
Before final experiments, add an experiment mode for the proposal-faithful term/paraphrase offset.

This will allow the final report to compare:

- term/paraphrase offset
- contextual sentence offset

That comparison is important because it turns an implementation divergence into an explicit methodological choice.
