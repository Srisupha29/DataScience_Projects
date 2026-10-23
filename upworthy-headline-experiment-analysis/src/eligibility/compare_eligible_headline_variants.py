
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

COMPARISON_PATH = ROOT / "data/processed/within_experiment_comparisons.parquet"
CANDIDATE_PATH = ROOT / "data/processed/comparison_candidates.parquet"

OUTPUT_PATH = ROOT / "data/processed/eligible_headline_variant_comparisons.csv"

EXPERIMENT_KEY = "experiment_id"
PACKAGE_KEY = "package_id"
HEADLINE_KEY = "normalized_headline"
ELIGIBILITY = "primary_headline_structural_eligible"


def main():
    comparisons = pd.read_parquet(COMPARISON_PATH)
    candidates = pd.read_parquet(CANDIDATE_PATH)

    eligible_ids = set(
        candidates.loc[candidates[ELIGIBILITY], "clickability_test_id"]
    )

    eligible = comparisons[
        comparisons[EXPERIMENT_KEY].isin(eligible_ids)
    ].copy()

    if eligible[PACKAGE_KEY].isna().any():
        raise ValueError("Missing package identities require investigation.")

    if eligible[HEADLINE_KEY].isna().any():
        raise ValueError("Missing normalized headlines require investigation.")

    if eligible[["impressions", "clicks"]].isna().any().any():
        raise ValueError("Missing impression or click metrics found.")

    if (eligible["impressions"] <= 0).any():
        raise ValueError("Non-positive impressions found.")

    if (
        (eligible["clicks"] < 0)
        | (eligible["clicks"] > eligible["impressions"])
    ).any():
        raise ValueError("Invalid click counts found.")

    # Determine whether an experiment contains any repeated package identity.
    identity_counts = (
        eligible.groupby([EXPERIMENT_KEY, PACKAGE_KEY])
        .size()
        .rename("identity_source_rows")
        .reset_index()
    )

    repeated_experiments = set(
        identity_counts.loc[
            identity_counts["identity_source_rows"] > 1,
            EXPERIMENT_KEY,
        ]
    )

    all_eligible_experiments = set(eligible[EXPERIMENT_KEY].unique())

    safe_ids = all_eligible_experiments - repeated_experiments

    # Retain only experiments where each package identity has one source row.
    clean = eligible[
        eligible[EXPERIMENT_KEY].isin(safe_ids)
    ].copy()

    if clean[PACKAGE_KEY].duplicated().any():
        # Package IDs are hashes of experiment + headline + image;
        # this global check is appropriate only if IDs are globally unique.
        # The authoritative check below validates within each experiment.
        duplicated_within_experiment = clean.duplicated(
            [EXPERIMENT_KEY, PACKAGE_KEY]
        )
        if duplicated_within_experiment.any():
            raise ValueError("Repeated package identity remains in comparison set.")

    # Recheck headline-only eligibility within the retained data.
    experiment_structure = (
        clean.groupby(EXPERIMENT_KEY)
        .agg(
            distinct_headlines=(HEADLINE_KEY, "nunique"),
            distinct_images=("image_id", "nunique"),
            missing_images=("image_id", lambda s: s.isna().sum()),
        )
    )

    structurally_valid_ids = set(
        experiment_structure.index[
            (experiment_structure["distinct_headlines"] > 1)
            & (experiment_structure["distinct_images"] == 1)
            & (experiment_structure["missing_images"] == 0)
        ]
    )

    clean = clean[
        clean[EXPERIMENT_KEY].isin(structurally_valid_ids)
    ].copy()

    # Compare each headline's recorded CTR against all other headlines
    # in the same retained experiment.
    clean["package_ctr"] = clean["clicks"] / clean["impressions"]

    experiment_totals = clean.groupby(EXPERIMENT_KEY).agg(
        experiment_clicks=("clicks", "sum"),
        experiment_impressions=("impressions", "sum"),
        headline_variants=(HEADLINE_KEY, "nunique"),
    )

    clean = clean.join(experiment_totals, on=EXPERIMENT_KEY)

    clean["other_clicks"] = clean["experiment_clicks"] - clean["clicks"]
    clean["other_impressions"] = (
        clean["experiment_impressions"] - clean["impressions"]
    )

    clean["other_headlines_ctr"] = (
        clean["other_clicks"] / clean["other_impressions"]
    )

    clean["ctr_difference_percentage_points"] = (
        clean["package_ctr"] - clean["other_headlines_ctr"]
    ) * 100

    clean["relative_ctr_difference_pct"] = (
        (
            clean["package_ctr"] / clean["other_headlines_ctr"]
        ) - 1
    ) * 100

    result_columns = [
        "row_id",
        EXPERIMENT_KEY,
        PACKAGE_KEY,
        "headline",
        "impressions",
        "clicks",
        "package_ctr",
        "headline_variants",
        "other_impressions",
        "other_clicks",
        "other_headlines_ctr",
        "ctr_difference_percentage_points",
        "relative_ctr_difference_pct",
    ]

    result = clean[result_columns].sort_values(
        [EXPERIMENT_KEY, "package_ctr"],
        ascending=[True, False],
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)

    print("=== Eligible headline variant comparison ===")
    print(f"Eligible experiments before exclusions: {len(all_eligible_experiments):,}")
    print(f"Experiments with repeated package identities: {len(repeated_experiments):,}")
    print(f"Experiments retained before structural recheck: {len(safe_ids):,}")
    print(f"Experiments compared: {result[EXPERIMENT_KEY].nunique():,}")
    print(f"Headline variant rows compared: {len(result):,}")
    print(f"Output: {OUTPUT_PATH}")

    print("\n=== Comparison coverage ===")
    print(
        "Experiments excluded for repeated identities:",
        len(repeated_experiments),
    )
    print(
        "Experiments retained but failing structural recheck:",
        len(safe_ids - structurally_valid_ids),
    )

    print("\n=== Descriptive differences vs. other headlines ===")
    print(
        result[
            [
                "ctr_difference_percentage_points",
                "relative_ctr_difference_pct",
            ]
        ].describe().round(3).to_string()
    )

    print(
        "\nLIMITATION: Comparisons are descriptive, not causal. "
        "Experiments with repeated package identities are excluded because "
        "their metric semantics remain unresolved. The remaining experiments "
        "still require documented assignment procedures before causal claims."
    )


if __name__ == "__main__":
    main()
