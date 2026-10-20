
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FEATURE_PATH = ROOT / "data/processed/headline_features.parquet"
CANDIDATE_PATH = ROOT / "data/processed/comparison_candidates.parquet"

features = pd.read_parquet(FEATURE_PATH)
candidates = pd.read_parquet(CANDIDATE_PATH)

KEY = "clickability_test_id"
ELIGIBILITY = "primary_headline_structural_eligible"

print("=== Input validation ===")
print(f"Feature rows: {len(features):,}")
print(f"Candidate experiments: {len(candidates):,}")
print(f"Feature experiment IDs missing: {features[KEY].isna().sum():,}")
print(f"Candidate IDs missing: {candidates[KEY].isna().sum():,}")
print(
    "Duplicate candidate experiment IDs:",
    int(candidates[KEY].duplicated().sum()),
)

if candidates[KEY].duplicated().any():
    raise ValueError("Candidate experiment IDs are not unique.")

if features[KEY].isna().any() or candidates[KEY].isna().any():
    raise ValueError("Missing experiment IDs require investigation.")

if ELIGIBILITY not in candidates.columns:
    raise ValueError(f"Missing eligibility column: {ELIGIBILITY}")

# Keep only the experiment ID and eligibility flag for the join.
lookup = candidates[[KEY, ELIGIBILITY]]

joined = features.merge(
    lookup,
    on=KEY,
    how="left",
    validate="many_to_one",
    indicator=True,
)

print("\n=== Join validation ===")
print(f"Rows after join: {len(joined):,}")
print(f"Row count preserved: {len(joined) == len(features)}")
print("\nJoin status:")
print(joined["_merge"].value_counts().to_string())

unmatched = joined.loc[
    joined["_merge"] != "both", KEY
].nunique()

print(f"\nUnmatched experiment IDs: {unmatched:,}")

print("\n=== Eligibility counts ===")
print(
    joined[ELIGIBILITY]
    .value_counts(dropna=False)
    .rename(index={True: "Eligible", False: "Not eligible"})
    .to_string()
)

print("\n=== Feature availability by eligibility ===")
print(
    joined.groupby(ELIGIBILITY, dropna=False)[
        ["headline_word_count", "headline_char_count"]
    ]
    .agg(["count", "mean", "median"])
    .round(2)
    .to_string()
)

if len(joined) != len(features):
    raise ValueError("Join changed the source row count.")

if unmatched:
    raise ValueError("Some feature rows did not match an experiment.")

if joined[ELIGIBILITY].isna().any():
    raise ValueError("Some rows have missing eligibility status.")

print("\nPASS: Join preserved all source rows and matched experiment eligibility.")

