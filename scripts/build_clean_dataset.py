from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


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

SOURCE_URL_MANUAL = ""
SOURCE_NAME_MANUAL = "project_manual_annotation"

DISALLOWED_SUBSTRINGS = {
    "fuck",
    "shit",
    "bitch",
    "ass ",
    " ass",
    "sex",
    "porn",
    "nude",
    "kill",
}

TARGET_CATEGORY_COUNTS = {
    "judgment": 14,
    "intensifier": 12,
    "emotion": 12,
    "performance": 12,
    "online": 12,
    "dating_social": 10,
    "appearance_style": 10,
    "agreement_discourse": 8,
    "action_event": 8,
    "other": 8,
}

MANUAL_NEUTRAL_SENTENCE_OVERRIDES = {
    "ex008": "She suddenly stopped replying after our second date.",
    "ex016": "He received far more criticism than support after that rude reply.",
    "ex023": "That was an admirably bold take in class today.",
    "ex033": "His appearance and confidence improved a lot over the last year.",
    "ex035": "You need to go outside and reconnect with real life after posting all day.",
    "ex049": "She performed stylishly and impressively at the showcase last night.",
    "ex050": "When he started talking about music theory, he spoke passionately at length.",
    "ex056": "That outfit resembles an early-2000s pop star.",
}

EXTERNAL_NEUTRAL_EXPRESSION_OVERRIDES = {
    "dank": "excellent",
    "tfw": "that feeling when",
    "woke": "politically aware",
    "bop": "excellent song",
    "big yikes": "very embarrassing",
    "camp": "ironically stylish",
    "snack": "attractive person",
    "periodt": "definitely",
    "facts": "true",
    "i oop": "awkward surprise",
    "sksksk": "excited laughter",
    "vibe check": "mood check",
    "irl": "in real life",
    "smh": "shaking my head",
    "say less": "say no more",
    "g2g": "got to go",
    "csl": "cannot stop laughing",
    "imoh": "in my humble opinion",
    "dtr": "define the relationship",
    "gg": "good game",
    "mte": "my thoughts exactly",
    "roflol": "laughing very hard",
    "ttfn": "goodbye for now",
    "wtg": "well done",
    "time": "tears in my eyes",
    "bff": "best friend",
    "1432": "I love you too",
    "2ez": "too easy",
}

CLEARLY_BAD_EXTERNAL_TERMS = {
    "high-key",
    "this ain’t it, chief",
    "ok boomer",
    "chad",
    "clown",
    "cringy",
    "naur",
    "cuffing",
    "gaup",
    "fomo",
    "low key",
    "afk",
    "atk",
    "atm",
    "ilu",
    "55555",
    "boujee",
    "tntl",
    "bak",
    "bbl",
    "brb",
    "ldr",
    "acpt",
}

CATEGORY_MAP = {
    "dating": "dating_social",
    "social": "dating_social",
    "fashion": "appearance_style",
    "style": "appearance_style",
    "appearance": "appearance_style",
    "opinion": "judgment",
    "truthfulness": "agreement_discourse",
    "agreement": "agreement_discourse",
    "hedge": "agreement_discourse",
    "temporal": "action_event",
    "academic": "action_event",
    "status": "other",
    "food": "other",
    "attitude": "judgment",
    "fandom": "other",
    "cognition": "emotion",
    "conversation": "action_event",
    "observation": "action_event",
    "action": "action_event",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the cleaned Eigenslang experiment dataset.")
    parser.add_argument("--manual", default="data/raw/slang_examples.csv")
    parser.add_argument("--external", default="data/processed/slang_examples_candidate_external.csv")
    parser.add_argument("--output", default="data/processed/slang_examples_clean.csv")
    parser.add_argument("--report", default="data/processed/slang_examples_clean_report.txt")
    parser.add_argument("--target-size", type=int, default=120)
    return parser.parse_args()


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    return re.sub(r"\s+", " ", text).strip()


def normalize_term(value: object) -> str:
    return normalize_text(value).strip("\"'“”‘’").lower()


def normalize_category(category: object) -> str:
    raw = normalize_text(category).lower()
    return CATEGORY_MAP.get(raw, raw or "other")


def manual_neutral_expression(paraphrase: str) -> str:
    text = normalize_text(paraphrase).strip(" .")
    return text


def replace_slang_in_sentence(sentence: str, slang: str, neutral: str) -> str:
    if not sentence:
        return ""
    pattern = slang_pattern(slang)
    if len(neutral.split()) > 8:
        return f"{sentence} Meaning: {neutral}."
    replaced = pattern.sub(neutral, sentence, count=1)
    if replaced == sentence:
        return f"{sentence} Meaning: {neutral}."
    return cleanup_sentence(replaced)


def slang_pattern(slang: str) -> re.Pattern[str]:
    escaped = re.escape(slang)
    if re.match(r"^[A-Za-z0-9]+$", slang):
        return re.compile(rf"\b{escaped}\b", flags=re.IGNORECASE)
    return re.compile(escaped, flags=re.IGNORECASE)


def cleanup_sentence(sentence: str) -> str:
    sentence = normalize_text(sentence)
    sentence = re.sub(r"\s+([,.!?])", r"\1", sentence)
    sentence = re.sub(r"\ban ([bcdfghjklmnpqrstvwxyz])", r"a \1", sentence, flags=re.I)
    return sentence


def standardize_manual(manual_path: Path) -> pd.DataFrame:
    df = pd.read_csv(manual_path)
    rows: list[dict[str, str]] = []
    for _, row in df.iterrows():
        slang = normalize_text(row["slang_term"])
        paraphrase = normalize_text(row["neutral_paraphrase"])
        sentence = normalize_text(row["context_sentence"])
        neutral_expression = manual_neutral_expression(paraphrase)
        row_id = normalize_text(row["id"])
        neutral_sentence = MANUAL_NEUTRAL_SENTENCE_OVERRIDES.get(
            row_id,
            replace_slang_in_sentence(sentence, slang, neutral_expression),
        )
        review_status = "manual_seed"
        if needs_sentence_review(sentence, neutral_sentence, neutral_expression):
            review_status = "manual_seed_neutral_sentence_review"

        rows.append(
            {
                "id": row_id,
                "slang_term": slang,
                "context_sentence": sentence,
                "neutral_expression": neutral_expression,
                "neutral_paraphrase": paraphrase,
                "neutral_sentence": neutral_sentence,
                "neutral_alternatives": "",
                "category": normalize_category(row["category"]),
                "source_type": normalize_text(row["source_type"]) or "manual",
                "source_name": SOURCE_NAME_MANUAL,
                "source_url": SOURCE_URL_MANUAL,
                "confidence": "high",
                "review_status": review_status,
                "notes": normalize_text(row["notes"]),
            }
        )
    return pd.DataFrame(rows, columns=CLEAN_COLUMNS)


def needs_sentence_review(original: str, neutral_sentence: str, neutral_expression: str) -> bool:
    lowered = neutral_sentence.lower()
    neutral_lower = neutral_expression.lower()
    if "meaning:" in lowered:
        return True
    if " got received " in lowered:
        return True
    if " a admirably " in lowered:
        return True
    if " stopped replying me " in lowered:
        return True
    if len(neutral_expression.split()) > 5 and neutral_lower in lowered:
        return True
    if original == neutral_sentence:
        return True
    return False


def quality_flags(row: pd.Series) -> list[str]:
    flags: list[str] = []
    text_blob = " ".join(
        normalize_text(row.get(column, ""))
        for column in ["slang_term", "context_sentence", "neutral_expression", "neutral_paraphrase"]
    ).lower()

    if any(bad in text_blob for bad in DISALLOWED_SUBSTRINGS):
        flags.append("sensitive_or_explicit")
    term_key = normalize_term(row["slang_term"])
    neutral_expression = normalize_text(row["neutral_expression"])
    if term_key in CLEARLY_BAD_EXTERNAL_TERMS:
        flags.append("manual_review_required")
    if len(neutral_expression.split()) > 5:
        flags.append("neutral_expression_too_long")
    if explanatory_neutral_expression(neutral_expression):
        flags.append("explanatory_neutral_expression")
    if len(normalize_text(row["slang_term"])) <= 1:
        flags.append("single_character_slang")
    if "meaning:" in normalize_text(row["neutral_sentence"]).lower():
        flags.append("neutral_sentence_needs_manual_rewrite")
    if normalize_text(row["confidence"]) == "low":
        flags.append("low_confidence")
    if not normalize_text(row["context_sentence"]) or not normalize_text(row["neutral_expression"]):
        flags.append("missing_core_field")
    return flags


def explanatory_neutral_expression(neutral_expression: str) -> bool:
    lowered = neutral_expression.lower()
    markers = [
        "describe ",
        "another way",
        "used to",
        "used for",
        "people who",
        "something that",
        "a person that",
        "term directed",
        "acronym for",
        "shortened version",
        "simply means",
        "means ",
    ]
    return any(marker in lowered for marker in markers)


def load_external_candidates(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=CLEAN_COLUMNS)
    df = pd.read_csv(path)
    for column in CLEAN_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[CLEAN_COLUMNS].copy()
    df["category"] = df["category"].map(normalize_category)
    df["review_status"] = "external_auto_cleaned"
    for idx, row in df.iterrows():
        term_key = normalize_term(row["slang_term"])
        if term_key in EXTERNAL_NEUTRAL_EXPRESSION_OVERRIDES:
            neutral = EXTERNAL_NEUTRAL_EXPRESSION_OVERRIDES[term_key]
            df.at[idx, "neutral_expression"] = neutral
            df.at[idx, "neutral_sentence"] = replace_slang_in_sentence(
                normalize_text(row["context_sentence"]),
                normalize_text(row["slang_term"]),
                neutral,
            )
    return df


def select_external(
    manual_df: pd.DataFrame,
    external_df: pd.DataFrame,
    target_size: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = manual_df.copy()
    rejected_rows: list[dict[str, str]] = []

    seen_terms = {normalize_term(term) for term in selected["slang_term"].tolist()}
    category_counts = selected["category"].value_counts().to_dict()
    slots_remaining = max(target_size - len(selected), 0)

    for _, row in external_df.iterrows():
        if slots_remaining <= 0:
            break

        term_key = normalize_term(row["slang_term"])
        flags = quality_flags(row)
        target_for_category = TARGET_CATEGORY_COUNTS.get(row["category"], TARGET_CATEGORY_COUNTS["other"])
        current_for_category = category_counts.get(row["category"], 0)

        if term_key in seen_terms:
            flags.append("duplicate_slang_term")
        if current_for_category >= target_for_category:
            flags.append("category_quota_full")

        if flags:
            rejected = row.to_dict()
            rejected["review_status"] = "rejected:" + "|".join(flags)
            rejected_rows.append(rejected)
            continue

        accepted = row.copy()
        accepted["id"] = f"ext{len(selected) - len(manual_df) + 1:04d}"
        accepted["review_status"] = "external_selected_auto"
        selected = pd.concat([selected, accepted.to_frame().T], ignore_index=True)
        seen_terms.add(term_key)
        category_counts[row["category"]] = current_for_category + 1
        slots_remaining -= 1

    rejected_df = pd.DataFrame(rejected_rows, columns=CLEAN_COLUMNS)
    return selected[CLEAN_COLUMNS], rejected_df


def write_report(clean_df: pd.DataFrame, rejected_df: pd.DataFrame, report_path: Path) -> None:
    lines = [
        "Eigenslang Clean Dataset Build Report",
        "",
        f"Clean rows: {len(clean_df)}",
        f"Rejected external rows recorded: {len(rejected_df)}",
        "",
        "Category counts:",
        clean_df["category"].value_counts().to_string(),
        "",
        "Source type counts:",
        clean_df["source_type"].value_counts().to_string(),
        "",
        "Review status counts:",
        clean_df["review_status"].value_counts().to_string(),
        "",
        "Confidence counts:",
        clean_df["confidence"].value_counts().to_string(),
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    manual_df = standardize_manual(Path(args.manual))
    external_df = load_external_candidates(Path(args.external))
    clean_df, rejected_df = select_external(manual_df, external_df, args.target_size)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(output_path, index=False)

    rejected_path = output_path.with_name(output_path.stem + "_rejected.csv")
    rejected_df.to_csv(rejected_path, index=False)

    report_path = Path(args.report)
    write_report(clean_df, rejected_df, report_path)

    print(f"Wrote {len(clean_df)} clean rows to {output_path.resolve()}")
    print(f"Wrote {len(rejected_df)} rejected rows to {rejected_path.resolve()}")
    print(f"Wrote report to {report_path.resolve()}")


if __name__ == "__main__":
    main()
