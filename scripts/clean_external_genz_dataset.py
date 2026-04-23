from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


OUTPUT_COLUMNS = [
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
    "notes",
]

SOURCE_NAME = "MLBtrio/genz-slang-dataset"
SOURCE_URL = "https://huggingface.co/datasets/MLBtrio/genz-slang-dataset"

EXCLUDE_TERMS = {
    # Explicit or sensitive entries are excluded to keep the course dataset clean.
    "bussy",
    "body count",
}

CATEGORY_KEYWORDS = [
    ("intensifier", ["emphasis", "emphasize", "intensify", "very", "really", "swear"]),
    ("emotion", ["angry", "upset", "jealous", "embarrass", "shock", "feeling", "laugh"]),
    ("performance", ["excellent", "high quality", "best", "impressive", "praise"]),
    ("online", ["internet", "meme", "social media", "tweet", "online", "platform"]),
    ("dating_social", ["dating", "relationship", "flirting", "attracted", "friends"]),
    ("appearance_style", ["fashion", "style", "outfit", "makeup", "looks", "aesthetic"]),
    ("judgment", ["bad", "good", "failure", "disapproval", "awkward", "cringe"]),
    ("agreement_discourse", ["agree", "confirm", "yes", "truth", "response"]),
    ("action_event", ["action", "event", "situation", "happen", "threaten"]),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean the external Gen Z slang dataset into the Eigenslang schema."
    )
    parser.add_argument(
        "--input",
        default="data/raw/external/mlbtrio_genz_slang_dataset.csv",
        help="Raw external CSV path.",
    )
    parser.add_argument(
        "--existing",
        default="data/raw/slang_examples.csv",
        help="Existing curated dataset used for deduplication.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/slang_examples_candidate_external.csv",
        help="Cleaned candidate output CSV path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=300,
        help="Maximum number of cleaned candidates to write.",
    )
    return parser.parse_args()


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    return re.sub(r"\s+", " ", text).strip()


def normalize_term(term: str) -> str:
    return normalize_text(term).strip("\"'“”‘’").lower()


def neutral_expression(description: str) -> str:
    cleaned = normalize_text(description)
    cleaned = re.sub(r"^(shorthand|shortened term|another way) for\s+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^used (to|when|for)\s+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^if someone is\s+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^if you\s+", "", cleaned, flags=re.I)
    cleaned = cleaned.strip(" .")
    if len(cleaned) > 70:
        cleaned = re.split(r"[.;]", cleaned)[0].strip()
    return cleaned[:120].strip()


def neutral_sentence(example: str, slang: str, neutral: str) -> str:
    if not example:
        return ""
    if len(neutral.split()) > 8:
        return cleanup_sentence(f"{example} Meaning: {neutral}.")

    pattern = slang_pattern(slang)
    replaced = pattern.sub(neutral, example, count=1)
    if replaced != example:
        return cleanup_sentence(replaced)
    return cleanup_sentence(f"{example} Meaning: {neutral}.")


def slang_pattern(slang: str) -> re.Pattern[str]:
    escaped = re.escape(slang)
    if re.match(r"^[A-Za-z0-9]+$", slang):
        return re.compile(rf"\b{escaped}\b", flags=re.IGNORECASE)
    return re.compile(escaped, flags=re.IGNORECASE)


def cleanup_sentence(sentence: str) -> str:
    sentence = normalize_text(sentence)
    sentence = re.sub(r"\s+([,.!?])", r"\1", sentence)
    return sentence


def infer_category(slang: str, description: str, context: str) -> str:
    haystack = f"{slang} {description} {context}".lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return category
    return "other"


def confidence_for_row(slang: str, example: str, neutral: str) -> str:
    if not slang or not example or not neutral:
        return "low"
    if len(neutral.split()) > 16:
        return "medium"
    if slang.lower() in example.lower():
        return "high"
    return "medium"


def load_existing_terms(path: Path) -> set[str]:
    if not path.exists():
        return set()
    df = pd.read_csv(path)
    if "slang_term" not in df.columns:
        return set()
    return {normalize_term(value) for value in df["slang_term"].dropna().tolist()}


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    existing_terms = load_existing_terms(Path(args.existing))

    if not input_path.exists():
        raise FileNotFoundError(f"Raw external dataset not found: {input_path}")

    raw_df = pd.read_csv(input_path)
    required = {"Slang", "Description", "Example", "Context"}
    missing = required - set(raw_df.columns)
    if missing:
        raise ValueError(f"External dataset is missing expected columns: {sorted(missing)}")

    rows: list[dict[str, str]] = []
    seen_terms: set[str] = set()

    for _, raw in raw_df.iterrows():
        slang = normalize_text(raw["Slang"])
        slang_key = normalize_term(slang)
        description = normalize_text(raw["Description"])
        example = normalize_text(raw["Example"])
        context = normalize_text(raw["Context"])

        if not slang_key or slang_key in EXCLUDE_TERMS:
            continue
        if slang_key in existing_terms or slang_key in seen_terms:
            continue
        if not description or not example:
            continue

        neutral = neutral_expression(description)
        if not neutral:
            continue

        seen_terms.add(slang_key)
        row_id = f"hf{len(rows) + 1:04d}"
        rows.append(
            {
                "id": row_id,
                "slang_term": slang,
                "context_sentence": example,
                "neutral_expression": neutral,
                "neutral_paraphrase": description,
                "neutral_sentence": neutral_sentence(example, slang, neutral),
                "neutral_alternatives": "",
                "category": infer_category(slang, description, context),
                "source_type": "external_dataset",
                "source_name": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "confidence": confidence_for_row(slang, example, neutral),
                "notes": context,
            }
        )

        if len(rows) >= args.limit:
            break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(output_path, index=False)

    print(f"Loaded {len(raw_df)} raw rows from {input_path}")
    print(f"Wrote {len(rows)} cleaned candidate rows to {output_path.resolve()}")
    print("Confidence counts:")
    print(pd.Series([row["confidence"] for row in rows]).value_counts().to_string())
    print("Category counts:")
    print(pd.Series([row["category"] for row in rows]).value_counts().to_string())


if __name__ == "__main__":
    main()
