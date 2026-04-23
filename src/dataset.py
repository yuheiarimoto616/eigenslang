from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

REQUIRED_COLUMNS = [
    "id",
    "slang_term",
    "context_sentence",
    "neutral_paraphrase",
    "category",
    "source_type",
    "notes",
]

OPTIONAL_CLEAN_COLUMNS = [
    "neutral_expression",
    "neutral_sentence",
    "neutral_alternatives",
    "source_name",
    "source_url",
    "confidence",
    "review_status",
]


@dataclass(frozen=True)
class DatasetSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def load_examples(csv_path: str | Path) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    df = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    for column in OPTIONAL_CLEAN_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    for column in REQUIRED_COLUMNS + OPTIONAL_CLEAN_COLUMNS:
        df[column] = df[column].fillna("").astype(str).str.strip()

    _validate_examples(df)
    return df


def _validate_examples(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("Dataset is empty.")

    if df["id"].duplicated().any():
        duplicate_ids = df.loc[df["id"].duplicated(), "id"].tolist()
        raise ValueError(f"Duplicate ids found: {duplicate_ids}")

    for column in ["id", "slang_term", "context_sentence", "neutral_paraphrase"]:
        empty_rows = df.index[df[column] == ""].tolist()
        if empty_rows:
            raise ValueError(f"Column '{column}' has empty values at rows: {empty_rows}")


def split_examples(
    df: pd.DataFrame,
    train_size: float = 0.6,
    validation_size: float = 0.2,
    test_size: float = 0.2,
    random_state: int = 440,
) -> DatasetSplit:
    total = train_size + validation_size + test_size
    if abs(total - 1.0) > 1e-9:
        raise ValueError("Split sizes must sum to 1.0")

    if len(df) < 6:
        raise ValueError("Need at least 6 examples before creating train/validation/test splits.")

    train_df, temp_df = train_test_split(
        df,
        train_size=train_size,
        random_state=random_state,
        shuffle=True,
    )

    validation_fraction = validation_size / (validation_size + test_size)
    validation_df, test_df = train_test_split(
        temp_df,
        train_size=validation_fraction,
        random_state=random_state,
        shuffle=True,
    )

    return DatasetSplit(
        train=train_df.reset_index(drop=True),
        validation=validation_df.reset_index(drop=True),
        test=test_df.reset_index(drop=True),
    )


def save_splits(split: DatasetSplit, output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    split.train.to_csv(path / "train.csv", index=False)
    split.validation.to_csv(path / "validation.csv", index=False)
    split.test.to_csv(path / "test.csv", index=False)
