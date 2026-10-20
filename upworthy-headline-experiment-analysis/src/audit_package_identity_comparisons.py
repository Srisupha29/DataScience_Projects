
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

COMPARISON_PATH = ROOT / "data/processed/within_experiment_comparisons.parquet"
CANDIDATE_PATH = ROOT / "data/processed/comparison_candidates.parquet"

EXPERIMENT_KEY = "experiment_id"
PACKAGE_KEY = "package_id"

comparisons = pd.read_parquet(COMPARISON_PATH)
candidates = pd.read_parquet(CANDIDATE_PATH)

eligible_ids = set(
    candidates.loc[
        candidates["primary_headline_structural_eligible"],
        "clickability_test_id",
    ]
)

eligible = comparisons[
    comparisons[EXPERIMENT_KEY].isin(eligible_ids)
].copy()

print("=== Package identity comparison audit ===")
print(f"Eligible experiments: {eligible[EXPERIMENT_KEY].nunique():,}")
print(f"Eligible source rows: {len(eligible):,}")
print(f"Distinct package identities: {eligible[PACKAGE_KEY].nunique():,}")

# Count source records per package identity within each experiment.
identity = (
    eligible.groupby([EXPERIMENT_KEY, PACKAGE_KEY], dropna=False)
    .agg(
        source_rows=("row_id", "size"),
        distinct_headlines=("normalized_headline", "nunique"),
        distinct_impressions=("impressions", "nunique"),
        distinct_click_counts=("clicks", "nunique"),
        min_impressions=("impressions", "min"),
        max_impressions=("impressions", "max"),
        min_clicks=("clicks", "min"),
        max_clicks=("clicks", "max"),
    )
    .reset_index()
)

repeated = identity[identity["source_rows"] > 1].copy()

print("\n=== Repeated package identities ===")
print(f"Identity groups: {len(identity):,}")
print(f"Repeated identity groups: {len(repeated):,}")
print(
    "Repeated groups with changing impressions:",
    int((repeated["distinct_impressions"] > 1).sum()),
)
print(
    "Repeated groups with changing clicks:",
    int((repeated["distinct_click_counts"] > 1).sum()),
)
print(
    "Repeated groups with changing headline text:",
    int((repeated["distinct_headlines"] > 1).sum()),
)

print("\n=== Source-row multiplicity per identity ===")
print(identity["source_rows"].value_counts().sort_index().to_string())

print("\n=== Repeated identity metric variation ===")
if repeated.empty:
    print("No repeated identities found in eligible experiments.")
else:
    print(
        repeated[
            [
                "source_rows",
                "distinct_impressions",
                "distinct_click_counts",
            ]
        ]
        .describe()
        .round(2)
        .to_string()
    )

print("\n=== Examples requiring semantic review ===")
examples = repeated[
    (repeated["distinct_impressions"] > 1)
    | (repeated["distinct_click_counts"] > 1)
].head(10)

if examples.empty:
    print("No repeated identities with changing metrics found.")
else:
    print(examples.to_string(index=False))

print(
    "\nDECISION: Do not sum or select a single repeated record automatically. "
    "Changing metrics mean that the valid package-level exposure and click "
    "counts cannot be established from identity alone."
)
