# Eigenslang Decision Log

Last updated: 2026-04-20

This file records the main project decisions and why they were made.

## D1. Keep the project as an empirical ML study
Decision:

- Treat `Eigenslang` as a hypothesis to test, not a theory to prove.

Reason:

- This matches the proposal and is more defensible for a course project.
- The report can still be strong even if results are negative.

## D2. Use one main task
Decision:

- The main task is slang normalization in context through retrieval of a neutral paraphrase.

Reason:

- It is concrete, measurable, and directly aligned with the proposal.
- It avoids overextending into generation or open-ended chatbot behavior.

## D3. Prioritize sentence-level or context-aware embeddings first
Decision:

- Start with embeddings that can represent the full context sentence instead of isolated slang tokens only.

Reason:

- Many proposed slang items are polysemous.
- Context-aware representations are more likely to make the evaluation meaningful.

## D4. Use simple baselines before any complex extension
Decision:

- Implement raw retrieval and mean-offset baselines before testing PCA/SVD.

Reason:

- Without these baselines, the main claim cannot be evaluated properly.
- If the baselines already fail catastrophically, that exposes a dataset or task-design issue early.

## D5. Keep dataset collection manual and modest
Decision:

- Build a curated dataset of roughly 80 to 120 examples.

Reason:

- Manual quality control matters more than scale here.
- The course report only needs enough data to support a careful experiment.

## D6. Accept negative results as valid
Decision:

- A negative result is acceptable if supported by controlled experiments and clear analysis.

Reason:

- The proposal already identifies heterogeneity and context dependence as real risks.
- This keeps the project honest and course-appropriate.

## D7. Align the whole project to the final report structure
Decision:

- Organize code, data, experiments, and notes around the paper sections required in `project-format/project.tex`.

Reason:

- This reduces last-minute writing friction.
- It ensures that every implementation task contributes to a reportable result.

## D8. Defer secondary ideas until the core pipeline works
Decision:

- Do not spend time on slang generation, large-scale scraping, or multiple model comparisons until the main pipeline is complete.

Reason:

- These are attractive but non-essential expansions.
- They increase implementation risk without improving the core argument enough.

## D9. Treat word2vec as an optional ablation, not the primary model
Decision:

- Do not switch the main experiment from sentence-transformer embeddings to word2vec by default.
- Consider word2vec only as a static word-vector baseline after evaluation design is improved.

Reason:

- Word2Vec is conceptually aligned with vector offsets and would be easy to explain in the report.
- However, it is static, word-level, and likely weak for recent, polysemous, and phrase-level slang.
- The current bottleneck is candidate-set design and task formulation, not the absence of another embedding model.
- If word2vec performs poorly, it may still be useful as evidence that contextual or phrase-level representations are needed.

## D10. Distinguish term/paraphrase offsets from contextual sentence offsets
Decision:

- Do not present the current implementation as exactly identical to the proposal's simplest \(s_i - n_i\) formulation.
- Document that the current code uses a context-preserving sentence offset.
- Add a proposal-faithful term/paraphrase offset mode before final experiments.

Reason:

- The proposal describes slang-expression embeddings minus neutral-paraphrase embeddings.
- The current implementation computes slang-sentence embeddings minus neutralized-sentence embeddings.
- This divergence is methodologically defensible because the dataset contains polysemous and phrase-level slang.
- Comparing both variants will make the final report more honest and stronger.
