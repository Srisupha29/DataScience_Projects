
from pathlib import Path

import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]

TARGET_PATH = ROOT / "data/processed/phase24_modeling_targets.csv"
FEATURE_PATH = ROOT / "data/processed/headline_features.parquet"
OUTPUT_PATH = ROOT / "data/processed/phase24_modeling_features.csv"

BINARY_FEATURES = [
    "contains_question_mark",
    "contains_exclamation_mark",
    "contains_number",
    "contains_you_family",
    "contains_first_person_pronoun",
    "contains_third_person_pronoun",
]

targets = pd.read_csv(TARGET_PATH)
source_features = pd.read_parquet(FEATURE_PATH)

# Keep only the existing Phase 2.2 headline features.
lookup = source_features[
    ["clickability_test_id", "headline"] + BINARY_FEATURES
].copy()

lookup = lookup.rename(
    columns={"clickability_test_id": "experiment_id"}
)

# Each experiment/headline pair must have one consistent feature vector.
lookup = lookup.drop_duplicates()

conflicts = lookup.duplicated(
    subset=["experiment_id", "headline"], keep=False
)

if conflicts.any():
    raise ValueError(
        "Some experiment/headline pairs have conflicting feature values. "
        "Inspect these before proceeding:\n"
        + lookup.loc[conflicts].head(10).to_string(index=False)
    )

lookup = lookup.drop_duplicates(
    subset=["experiment_id", "headline"]
)

data = targets.merge(
    lookup,
    on=["experiment_id", "headline"],
    how="left",
    validate="many_to_one",
    indicator=True,
)

unmatched = data["_merge"] != "both"

if unmatched.any():
    raise ValueError(
        f"{unmatched.sum()} target rows have no matching Phase 2.2 "
        "headline features. Do not silently discard them."
    )

data = data.drop(columns="_merge")

for feature in BINARY_FEATURES:
    if data[feature].isna().any():
        raise ValueError(f"Missing values in {feature}")

    data[feature] = data[feature].astype("int8")

# Save the row-level modeling data. TF-IDF is generated separately
# within each training fold during model evaluation.
data.to_csv(OUTPUT_PATH, index=False)

# Smoke test only: demonstrate the combined sparse feature matrix.
# This full-data fit is NOT used for cross-validation or final metrics.
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_features=5000,
    sublinear_tf=True,
)

text_matrix = vectorizer.fit_transform(data["headline"].fillna(""))
numeric_matrix = csr_matrix(data[BINARY_FEATURES].to_numpy())

combined_matrix = hstack(
    [text_matrix, numeric_matrix],
    format="csr",
)

print("FEATURE BUILD VALIDATION")
print(f"Rows: {len(data):,}")
print(f"Experiments: {data['experiment_id'].nunique():,}")
print(f"Matched Phase 2.2 feature rows: {len(data):,}")
print(f"Binary headline features: {len(BINARY_FEATURES)}")
print(f"TF-IDF vocabulary size: {len(vectorizer.vocabulary_):,}")
print(f"TF-IDF matrix shape: {text_matrix.shape}")
print(f"Combined sparse matrix shape: {combined_matrix.shape}")
print("\nTarget distribution:")
print(data["target"].value_counts().sort_index().to_string())
print(f"\nSaved: {OUTPUT_PATH}")
