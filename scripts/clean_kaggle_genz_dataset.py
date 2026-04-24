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

SOURCE_NAME = "Kaggle: Gen Z words and Phrases Dataset"
SOURCE_URL = "https://www.kaggle.com/datasets/tawfiayeasmin/gen-z-words-and-phrases-dataset"

CATEGORY_KEYWORDS = [
    ("intensifier", ["very", "really", "openly", "emphatically", "seriously"]),
    ("emotion", ["angry", "shocked", "surprised", "frustrated", "excited", "upset", "nervous"]),
    ("performance", ["good", "excellent", "skillfully", "impressive", "well done", "success"]),
    ("online", ["social media", "message", "internet", "meme", "post", "online"]),
    ("dating_social", ["someone they like", "relationship", "date", "dating", "attractive", "flirting"]),
    ("appearance_style", ["style", "fashion", "outfit", "looks", "appearance", "aesthetic"]),
    ("judgment", ["awkward", "embarrassing", "bad", "weird", "disapproval", "criticized"]),
    ("agreement_discourse", ["true", "agree", "honestly", "for real", "definitely"]),
    ("action_event", ["leave", "exit", "handle", "situation", "happened", "event"]),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean the Kaggle Gen Z words dataset into the Eigenslang schema."
    )
    parser.add_argument(
        "--input",
        default="data/raw/external/gen_zz_words.csv",
        help="Raw Kaggle CSV path.",
    )
    parser.add_argument(
        "--existing",
        default="data/raw/slang_examples.csv",
        help="Existing curated dataset used for deduplication.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/slang_examples_candidate_kaggle.csv",
        help="Cleaned candidate output CSV path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=250,
        help="Maximum number of cleaned candidates to write.",
    )
    return parser.parse_args()


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip("\"'“”‘’")


def normalize_term(value: object) -> str:
    return normalize_text(value).lower()


def slang_pattern(slang: str) -> re.Pattern[str]:
    escaped = re.escape(slang)
    if re.match(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$", slang):
        return re.compile(rf"\b{escaped}\b", flags=re.IGNORECASE)
    return re.compile(escaped, flags=re.IGNORECASE)


def cleanup_sentence(sentence: str) -> str:
    sentence = normalize_text(sentence)
    sentence = re.sub(r"\s+([,.!?])", r"\1", sentence)
    return sentence


def load_existing_terms(path: Path) -> set[str]:
    if not path.exists():
        return set()
    df = pd.read_csv(path)
    if "slang_term" not in df.columns:
        return set()
    return {normalize_term(value) for value in df["slang_term"].dropna().tolist()}


def normalize_definition(definition: str) -> str:
    cleaned = normalize_text(definition).strip(" .")
    cleaned = re.sub(r"^to\s+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^someone who is\s+", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^someone who does too much for someone they like$", "overly devoted admirer", cleaned, flags=re.I)
    cleaned = re.sub(r"^a song that's really good$", "excellent song", cleaned, flags=re.I)
    cleaned = re.sub(r"^direct message on social media$", "direct message", cleaned, flags=re.I)
    return cleaned[:120].strip()


def neutral_sentence(example: str, slang: str, neutral: str) -> str:
    if not example:
        return ""
    if len(neutral.split()) > 8:
        return cleanup_sentence(f"{example} Meaning: {neutral}.")
    replaced = slang_pattern(slang).sub(neutral, example, count=1)
    if replaced != example:
        return cleanup_sentence(replaced)
    return cleanup_sentence(f"{example} Meaning: {neutral}.")


def infer_category(slang: str, definition: str, popularity: str) -> str:
    haystack = f"{slang} {definition} {popularity}".lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return category
    return "other"


def confidence_for_row(slang: str, example: str, neutral: str, popularity: str) -> str:
    if not slang or not example or not neutral:
        return "low"
    if slang.lower() not in example.lower():
        return "medium"
    if normalize_text(popularity).lower() == "high" and len(neutral.split()) <= 5:
        return "high"
    return "medium"


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    existing_terms = load_existing_terms(Path(args.existing))

    if not input_path.exists():
        raise FileNotFoundError(f"Raw Kaggle dataset not found: {input_path}")

    raw_df = pd.read_csv(input_path)
    required = {"Word/Phrase", "Definition", "Example Sentence", "Popularity/Trend Level"}
    missing = required - set(raw_df.columns)
    if missing:
        raise ValueError(f"Kaggle dataset is missing expected columns: {sorted(missing)}")

    rows: list[dict[str, str]] = []
    seen_terms: set[str] = set()

    for _, raw in raw_df.iterrows():
        slang = normalize_text(raw["Word/Phrase"])
        slang_key = normalize_term(slang)
        definition = normalize_text(raw["Definition"])
        example = normalize_text(raw["Example Sentence"])
        popularity = normalize_text(raw["Popularity/Trend Level"])

        if not slang_key or not definition or not example:
            continue
        if slang_key in existing_terms or slang_key in seen_terms:
            continue

        neutral = normalize_definition(definition)
        if not neutral:
            continue

        row_id = f"kg{len(rows) + 1:04d}"
        rows.append(
            {
                "id": row_id,
                "slang_term": slang,
                "context_sentence": example,
                "neutral_expression": neutral,
                "neutral_paraphrase": definition,
                "neutral_sentence": neutral_sentence(example, slang, neutral),
                "neutral_alternatives": "",
                "category": infer_category(slang, definition, popularity),
                "source_type": "external_dataset",
                "source_name": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "confidence": confidence_for_row(slang, example, neutral, popularity),
                "notes": f"popularity={popularity}" if popularity else "",
            }
        )
        seen_terms.add(slang_key)

        if len(rows) >= args.limit:
            break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(output_path, index=False)

    print(f"Loaded {len(raw_df)} raw rows from {input_path}")
    print(f"Wrote {len(rows)} cleaned candidate rows to {output_path.resolve()}")
    print("Confidence counts:")
    print(pd.Series([row['confidence'] for row in rows]).value_counts().to_string())
    print("Category counts:")
    print(pd.Series([row['category'] for row in rows]).value_counts().to_string())


if __name__ == "__main__":
    main()
