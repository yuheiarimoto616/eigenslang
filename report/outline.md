# Final Report Outline

Use this outline when converting the project into the final CPSC 440 report.

## 1. Introduction

- What problem are we solving?
- Why youth slang normalization matters for NLP
- Why existing lexical resources and standard embeddings are insufficient
- Main contribution and one-sentence summary of findings

## 2. Related Work

- slang-specific resources and embeddings
- embedding-space interpretation or eigenvector analysis
- prior work on slang normalization, generation, or social-media semantics

## 3. Dataset and Task

- dataset construction
- annotation decisions
- example format
- train, validation, and test split
- retrieval task definition

## 4. Methods

- embedding representation
- raw retrieval baseline
- mean-offset baseline
- `Eigenslang` PCA or SVD method
- validation and hyperparameter tuning

## 5. Experiments

- experimental setup
- metrics: Top-1 and Top-3
- main quantitative results
- ablations or optional multi-component comparison

## 6. Analysis

- what the top principal component seems to capture
- representative successes
- representative failures
- error categories

## 7. Discussion and Limitations

- strongest result
- main weakness
- whether a shared slang direction appears to exist
- what a larger follow-up project would do differently

## 8. Conclusion

- concise answer to the project question
- final take-away for NLP and slang normalization
