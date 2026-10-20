
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FEATURE_PATH = ROOT / "data/processed/headline_features.parquet"
CANDIDATE_PATH = ROOT / "data/processed/comparison_candidates.parquet"
OUTPUT_PATH = ROOT / "data/processed/headline_feature_ctr_summary.csv"

EXPERIMENT_KEY = "clickability_test_id"
ELIGIBILITY = "primary_headline_structural_eligible"

BINARY_FEATURES = {
    "Question mark": "contains_question_mark",
    "Exclamation mark": "contains_exclamation_mark",
    "Contains number": "contains_number",
    "You-family pronoun": "contains_you_family",
    "First-person pronoun": "contains_first_person_pronoun",
    "Third-person pronoun": "contains_third_person_pronoun",
}

# These bins make the continuous features easier to interpret.
# They are descriptive groupings, not optimized thresholds.
NUMERIC_BINS = {
    "Headline word count": (
        "headline_word_count",
        [-float("inf"), 10, 14, 17, float("inf")],
        ["10 or fewer", "11–14", "15–17", "18 or more"],
    ),
    "Headline character count": (
        "headline_char_count",
        [-float("inf"), 70, 84, 94, float("inf")],
        ["70 or fewer", "71–84", "85–94", "95 or more"],
    ),
}


def summarize_group(
    data: pd.DataFrame,
    feature_name: str,
    group_name: str,
) -> dict:
    impressions = data["impressions"].sum()
    clicks = data["clicks"].sum()

    return {
        "feature": feature_name,
        "group": group_name,
        "source_rows": len(data),
        "experiments": data[EXPERIMENT_KEY].nunique(),
        "total_impressions": int(impressions),
        "total_clicks": int(clicks),
        "pooled_ctr": clicks / impressions if impressions > 0 else float("nan"),
    }


def main():
    features = pd.read_parquet(FEATURE_PATH)
    candidates = pd.read_parquet(CANDIDATE_PATH)

    required_features = {
        EXPERIMENT_KEY,
        "impressions",
        "clicks",
        *BINARY_FEATURES.values(),
        *(spec[0] for spec in NUMERIC_BINS.values()),
    }

    missing = required_features - set(features.columns)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")

    if candidates[EXPERIMENT_KEY].duplicated().any():
        raise ValueError("Candidate experiment IDs must be unique.")

    if candidates[EXPERIMENT_KEY].isna().any():
        raise ValueError("Candidate experiment IDs contain missing values.")

    if features[EXPERIMENT_KEY].isna().any():
        raise ValueError("Feature experiment IDs contain missing values.")

    # Join only the eligibility flag; validate the expected many-to-one join.
    eligible_lookup = candidates[
        [EXPERIMENT_KEY, ELIGIBILITY]
    ]

    data = features.merge(
        eligible_lookup,
        on=EXPERIMENT_KEY,
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    if not data["_merge"].eq("both").all():
        raise ValueError("Some feature rows did not match candidate experiments.")

    if data[ELIGIBILITY].isna().any():
        raise ValueError("Some rows have missing eligibility status.")

    data = data.loc[data[ELIGIBILITY]].copy()

    if data.empty:
        raise ValueError("No structurally eligible rows were found.")

    # Validate the metrics before calculating CTR.
    if data[["impressions", "clicks"]].isna().any().any():
        raise ValueError("Missing impression or click counts found.")

    if (data["impressions"] <= 0).any():
        raise ValueError(
            "Non-positive impressions found. Inspect these rows before analysis."
        )

    if (data["clicks"] < 0).any():
        raise ValueError("Negative click counts found.")

    if (data["clicks"] > data["impressions"]).any():
        raise ValueError("Clicks exceed impressions in at least one source row.")

    summaries = []

    # Binary features: compare rows with versus without each characteristic.
    for display_name, column in BINARY_FEATURES.items():
        for value, group in data.groupby(column, dropna=False):
            if pd.isna(value):
                label = "Missing"
            else:
                label = "Yes" if bool(value) else "No"

            summaries.append(
                summarize_group(group, display_name, label)
            )

    # Continuous features: compare predefined length groups.
    for display_name, (column, bins, labels) in NUMERIC_BINS.items():
        categories = pd.cut(
            data[column],
            bins=bins,
            labels=labels,
            include_lowest=True,
        )

        for label, group in data.groupby(categories, observed=False):
            if len(group) == 0:
                continue

            summaries.append(
                summarize_group(group, display_name, str(label))
            )

    result = pd.DataFrame(summaries)

    # Keep CTR as a decimal in the CSV (e.g. 0.015 means 1.5%).
    result = result.sort_values(
        ["feature", "group"],
        kind="stable",
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False)

    print("=== Headline feature CTR analysis ===")
    print(f"Eligible source rows: {len(data):,}")
    print(f"Eligible experiments: {data[EXPERIMENT_KEY].nunique():,}")
    print(f"Total recorded impressions: {data['impressions'].sum():,}")
    print(f"Total recorded clicks: {data['clicks'].sum():,}")
    print(f"Output: {OUTPUT_PATH}")

    print("\n=== Exploratory CTR summaries ===")
    display = result.copy()
    display["pooled_ctr_pct"] = display["pooled_ctr"] * 100
    display = display.drop(columns="pooled_ctr")

    print(
        display.to_string(
            index=False,
            formatters={
                "pooled_ctr_pct": lambda value: f"{value:.3f}%"
            },
        )
    )

    print(
        "\nLIMITATION: These are source-row-level pooled CTR summaries. "
        "Repeated records may contain changing metrics and are not confirmed "
        "to represent independent observations. Differences are exploratory, "
        "not causal or inferential conclusions."
    )


if __name__ == "__main__":
    main()
