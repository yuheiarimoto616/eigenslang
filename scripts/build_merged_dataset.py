from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CURATED_KAGGLE_TERMS = [
    "Bounce",
    "Cancelled",
    "DM",
    "Dope",
    "Finesse",
    "Gassed Up",
    "Gucci",
    "High-Key",
    "Hypebeast",
    "Living Rent-Free",
    "Normalize",
    "Receipts",
    "Shooketh",
    "Thirsty",
    "Tight",
    "Unbothered",
]

CLEAN_COLUMNS = [
    "id",
    "slang_term",
    "context_sentence",
    "neutral_expression",
    "neutral_paraphrase",
    "neutral_sentence",
    "neutral_alternatives",
    "category",
    "source_type",
    "source_name",
    "source_url",
    "confidence",
    "review_status",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge curated Kaggle rows into the main clean dataset.")
    parser.add_argument("--base", default="data/processed/slang_examples_clean.csv")
    parser.add_argument("--kaggle", default="data/processed/slang_examples_candidate_kaggle.csv")
    parser.add_argument("--output", default="data/processed/slang_examples_clean_merged.csv")
    parser.add_argument("--report", default="data/processed/slang_examples_clean_merged_report.txt")
    return parser.parse_args()


def normalize_term(value: object) -> str:
    return str(value).strip().lower()


def load_base(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in CLEAN_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[CLEAN_COLUMNS].copy()


def load_kaggle(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in CLEAN_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[CLEAN_COLUMNS].copy()


def curated_kaggle_rows(base_df: pd.DataFrame, kaggle_df: pd.DataFrame) -> pd.DataFrame:
    seen_terms = {normalize_term(term) for term in base_df["slang_term"].tolist()}
    selected = kaggle_df[kaggle_df["slang_term"].isin(CURATED_KAGGLE_TERMS)].copy()
    selected = selected[~selected["slang_term"].map(normalize_term).isin(seen_terms)].copy()
    order = {term: i for i, term in enumerate(CURATED_KAGGLE_TERMS)}
    selected["_order"] = selected["slang_term"].map(order)
    selected = selected.sort_values("_order").drop(columns="_order")

    rows = []
    for index, (_, row) in enumerate(selected.iterrows(), start=1):
        row = row.copy()
        row["id"] = f"kgmerge{index:03d}"
        row["review_status"] = "external_selected_kaggle_curated"
        rows.append(row.to_dict())

    return pd.DataFrame(rows, columns=CLEAN_COLUMNS)


def write_report(base_df: pd.DataFrame, added_df: pd.DataFrame, merged_df: pd.DataFrame, report_path: Path) -> None:
    lines = [
        "Eigenslang Merged Dataset Report",
        "",
        f"Base rows: {len(base_df)}",
        f"Curated Kaggle rows added: {len(added_df)}",
        f"Merged rows: {len(merged_df)}",
        "",
        "Added Kaggle terms:",
        ", ".join(added_df["slang_term"].tolist()),
        "",
        "Merged category counts:",
        merged_df["category"].value_counts().to_string(),
        "",
        "Merged source counts:",
        merged_df["source_name"].value_counts().to_string(),
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    base_df = load_base(Path(args.base))
    kaggle_df = load_kaggle(Path(args.kaggle))
    added_df = curated_kaggle_rows(base_df, kaggle_df)
    merged_df = pd.concat([base_df, added_df], ignore_index=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(output_path, index=False)

    report_path = Path(args.report)
    write_report(base_df, added_df, merged_df, report_path)

    print(f"Wrote {len(merged_df)} merged rows to {output_path.resolve()}")
    print(f"Added {len(added_df)} curated Kaggle rows")
    print(f"Wrote report to {report_path.resolve()}")


if __name__ == "__main__":
    main()
