from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ABBREVIATION_TERMS = {
    "1432",
    "2ez",
    "af",
    "afpoe",
    "bff",
    "bffr",
    "csl",
    "cu",
    "cul8r",
    "dm",
    "dtr",
    "fr",
    "g2g",
    "gg",
    "gn",
    "imoh",
    "irl",
    "lmao",
    "mte",
    "npc",
    "roflol",
    "smh",
    "tfw",
    "time",
    "ttfn",
    "u4e",
    "wtg",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an abbreviation-filtered variant of the merged slang dataset."
    )
    parser.add_argument("--input", default="data/processed/slang_examples_clean_merged.csv")
    parser.add_argument("--output", default="data/processed/slang_examples_clean_no_abbrev.csv")
    parser.add_argument(
        "--report",
        default="data/processed/slang_examples_clean_no_abbrev_report.txt",
    )
    return parser.parse_args()


def normalize_term(value: object) -> str:
    return str(value).strip().lower()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)

    df = pd.read_csv(input_path)
    keep_mask = ~df["slang_term"].map(normalize_term).isin(ABBREVIATION_TERMS)
    filtered_df = df[keep_mask].copy()
    removed_df = df[~keep_mask].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    filtered_df.to_csv(output_path, index=False)

    removed_path = output_path.with_name(output_path.stem + "_removed.csv")
    removed_df.to_csv(removed_path, index=False)

    lines = [
        "Eigenslang Abbreviation-Filtered Dataset Report",
        "",
        f"Input rows: {len(df)}",
        f"Filtered rows: {len(filtered_df)}",
        f"Removed abbreviation-like rows: {len(removed_df)}",
        "",
        "Removed terms:",
        ", ".join(removed_df["slang_term"].astype(str).tolist()),
        "",
        "Filtered category counts:",
        filtered_df["category"].value_counts().to_string(),
        "",
        "Removed category counts:",
        removed_df["category"].value_counts().to_string() if not removed_df.empty else "",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {len(filtered_df)} filtered rows to {output_path.resolve()}")
    print(f"Wrote {len(removed_df)} removed rows to {removed_path.resolve()}")
    print(f"Wrote report to {report_path.resolve()}")


if __name__ == "__main__":
    main()
