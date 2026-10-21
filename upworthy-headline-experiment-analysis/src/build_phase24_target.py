
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

COMPARISON_PATH = (
    ROOT / "data/processed/eligible_headline_variant_comparisons.csv"
)
PACKAGE_PATH = ROOT / "data/processed/packages.parquet"
OUTPUT_PATH = ROOT / "data/processed/phase24_modeling_targets.csv"

comparisons = pd.read_csv(COMPARISON_PATH)
packages = pd.read_parquet(PACKAGE_PATH)

# Attach only stable package metadata. Do not join repeated measurement rows.
metadata = packages[
    [
        "package_id",
        "clickability_test_id",
        "normalized_headline",
        "eyecatcher_id",
    ]
].drop_duplicates()

assert metadata["package_id"].is_unique, (
    "Package metadata is not unique by package_id."
)

data = comparisons.merge(
    metadata,
    on="package_id",
    how="left",
    validate="one_to_one",
)

assert data["normalized_headline"].notna().all()
assert data["eyecatcher_id"].notna().all()
assert (
    data["experiment_id"] == data["clickability_test_id"]
).all()

# Apply the checklist's operational headline-only eligibility rule.
experiment_audit = metadata.groupby("clickability_test_id").agg(
    distinct_headlines=("normalized_headline", "nunique"),
    distinct_images=("eyecatcher_id", "nunique"),
)

eligible_experiments = experiment_audit.index[
    (experiment_audit["distinct_headlines"] >= 2)
    & (experiment_audit["distinct_images"] == 1)
]

data = data[
    data["experiment_id"].isin(eligible_experiments)
].copy()

# Reconstruct the label from underlying counts.
assert (data["impressions"] > 0).all()
assert (data["other_impressions"] > 0).all()
assert data[["clicks", "other_clicks"]].notna().all().all()

data["relative_ctr"] = (
    data["clicks"] / data["impressions"]
    - data["other_clicks"] / data["other_impressions"]
)

data["target"] = (data["relative_ctr"] > 0).astype("int8")

assert (
    data["target"]
    == data["ctr_difference_percentage_points"].gt(0).astype("int8")
).all()

# Keep outcomes for auditing, but do not use them as model predictors.
data = data.drop(columns=["clickability_test_id"])

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
data.to_csv(OUTPUT_PATH, index=False)

print("TARGET DATASET CREATED")
print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
print(f"Rows: {len(data):,}")
print(f"Experiments: {data['experiment_id'].nunique():,}")
print(f"Unique package IDs: {data['package_id'].nunique():,}")
print("\nTarget distribution:")
print(data["target"].value_counts().sort_index().to_string())
print("\nTarget proportions:")
print(data["target"].value_counts(normalize=True).sort_index().round(4).to_string())
print("\nHeadline-only eligibility violations:", (
    (data.groupby("experiment_id")["normalized_headline"].nunique() < 2).sum()
    + (data.groupby("experiment_id")["eyecatcher_id"].nunique() != 1).sum()
))
print(f"\nSaved: {OUTPUT_PATH}")
