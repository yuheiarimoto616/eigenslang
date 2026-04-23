from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download


DATASET_ID = "MLBtrio/genz-slang-dataset"
DEFAULT_FILENAME = "all_slangs.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the MLBtrio/genz-slang-dataset CSV from Hugging Face."
    )
    parser.add_argument(
        "--repo-id",
        default=DATASET_ID,
        help="Hugging Face dataset repository id.",
    )
    parser.add_argument(
        "--filename",
        default=DEFAULT_FILENAME,
        help="Dataset filename inside the Hugging Face repository.",
    )
    parser.add_argument(
        "--output",
        default="data/raw/external/mlbtrio_genz_slang_dataset.csv",
        help="Output CSV path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    downloaded = hf_hub_download(
        repo_id=args.repo_id,
        repo_type="dataset",
        filename=args.filename,
    )

    df = pd.read_csv(downloaded)
    df.to_csv(output_path, index=False)

    print(f"Downloaded {len(df)} rows from {args.repo_id}/{args.filename}")
    print(f"Saved raw external dataset to {output_path.resolve()}")
    print(f"Columns: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()
