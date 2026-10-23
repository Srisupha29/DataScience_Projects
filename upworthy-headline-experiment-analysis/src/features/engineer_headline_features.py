from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data/raw/upworthy-archive-exploratory-packages-03.12.2020.csv"
OUTPUT_PATH = ROOT / "data/processed/headline_features.parquet"

df = pd.read_csv(RAW_PATH)

if "headline" not in df.columns:
    raise ValueError("The source CSV does not contain a 'headline' column.")

# Preserve the original headline and source rows.
headline = df["headline"].fillna("").astype(str)

def count_pattern(text, pattern):
    return len(re.findall(pattern, text, flags=re.IGNORECASE))

# Word-like tokens, including contractions and hyphenated words.
WORD_PATTERN = r"\b[\w]+(?:['’\-][\w]+)*\b"

df["headline_char_count"] = headline.str.len()
df["headline_word_count"] = headline.apply(
    lambda text: len(re.findall(WORD_PATTERN, text))
)

df["question_mark_count"] = headline.str.count(r"\?")
df["exclamation_mark_count"] = headline.str.count("!")
df["contains_question_mark"] = df["question_mark_count"] > 0
df["contains_exclamation_mark"] = df["exclamation_mark_count"] > 0

df["number_count"] = headline.apply(
    lambda text: count_pattern(text, r"\d+")
)
df["contains_number"] = df["number_count"] > 0

# Pronouns are counted as whole words, not as partial matches inside other words.
pronoun_groups = {
    "you_family_count": r"\b(?:you|your|yours|yourself|yourselves)\b",
    "first_person_count": r"\b(?:i|me|my|mine|myself|we|us|our|ours|ourselves)\b",
    "third_person_count": r"\b(?:he|him|his|himself|she|her|hers|herself|they|them|their|theirs|themselves)\b",
}

for feature, pattern in pronoun_groups.items():
    df[feature] = headline.apply(
        lambda text: count_pattern(text, pattern)
    )

df["contains_you_family"] = df["you_family_count"] > 0
df["contains_first_person_pronoun"] = df["first_person_count"] > 0
df["contains_third_person_pronoun"] = df["third_person_count"] > 0

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUTPUT_PATH, index=False)

print("=== Headline feature engineering ===")
print(f"Source rows: {len(df):,}")
print(f"Missing headlines: {int(df['headline'].isna().sum()):,}")
print(f"Output: {OUTPUT_PATH}")
print(f"Output rows: {len(df):,}")

feature_columns = [
    "headline_char_count",
    "headline_word_count",
    "question_mark_count",
    "exclamation_mark_count",
    "number_count",
    "you_family_count",
    "first_person_count",
    "third_person_count",
]

print("\n=== Numeric feature summary ===")
print(df[feature_columns].describe().round(2).to_string())

print("\n=== Feature prevalence ===")
binary_columns = [
    "contains_question_mark",
    "contains_exclamation_mark",
    "contains_number",
    "contains_you_family",
    "contains_first_person_pronoun",
    "contains_third_person_pronoun",
]

for column in binary_columns:
    count = int(df[column].sum())
    print(f"{column}: {count:,} rows ({count / len(df):.1%})")

print("\n=== Example rows ===")
print(
    df[["headline"] + feature_columns].head(5).to_string(index=False)
)
