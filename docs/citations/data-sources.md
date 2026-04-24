# Data Sources To Cite

Date added: 2026-04-23

## MLBtrio/genz-slang-dataset

Use in project:

- candidate external source for expanding the Eigenslang dataset
- source fields include slang term, description, example sentence, and context notes
- imported rows should be treated as candidates and manually/semiautomatically cleaned before final experiments

URL:

- https://huggingface.co/datasets/MLBtrio/genz-slang-dataset

Observed dataset metadata from Hugging Face:

- repository: `MLBtrio/genz-slang-dataset`
- format: CSV
- language: English
- size class: 1K-10K
- dataset viewer reports about 1.78k rows
- visible fields: `Slang`, `Description`, `Example`, `Context`

Citation note for report:

- Cite this dataset if any imported or cleaned rows are used in final experiments.
- State that the dataset was used as a source pool and that examples were cleaned/filtered into the project schema.

License note:

- The license was not clearly visible during initial inspection of the Hugging Face page.
- Before final submission, check the dataset card/files again and report any available license information accurately.

## Gen Z words and Phrases Dataset

Use in project:

- additional external source for testing whether conclusions persist across datasets
- source fields include slang term, definition, example sentence, and popularity/trend level
- imported rows were mapped into the Eigenslang schema and filtered before experiments

URL:

- https://www.kaggle.com/datasets/tawfiayeasmin/gen-z-words-and-phrases-dataset

Observed dataset metadata from Kaggle:

- title: `Gen Z words and Phrases Dataset`
- file: `gen_zz_words.csv`
- visible fields: `Word/Phrase`, `Definition`, `Example Sentence`, `Popularity/Trend Level`
- dataset page description reports about 500 terms, but the imported CSV in this project contained 204 rows and 90 unique terms

Citation note for report:

- Cite the Kaggle dataset if the Kaggle-derived cleaned rows are used in experiments or discussed as a comparison dataset.
- State clearly that the raw file was cleaned and reduced before use in the project pipeline.

License note:

- The Kaggle dataset page lists the license as MIT.
