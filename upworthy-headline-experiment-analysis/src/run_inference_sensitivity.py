from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

COMPARISON_FILE = PROCESSED / "eligible_headline_variant_comparisons.csv"
FEATURE_FILE = PROCESSED / "headline_features.parquet"
BALANCE_FILE = PROCESSED / "impression_balance.parquet"

TESTS_FILE = PROCESSED / "phase23_sensitivity_tests.csv"
SUMMARY_FILE = PROCESSED / "phase23_sensitivity_summary.csv"

FEATURES = [
    "contains_question_mark",
    "contains_exclamation_mark",
    "contains_number",
    "contains_you_family",
    "contains_first_person_pronoun",
    "contains_third_person_pronoun",
]

BOOTSTRAP_REPS = 10_000
RANDOM_SEED = 20261021


def two_proportion_pvalue(clicks_yes, impressions_yes, clicks_no, impressions_no):
    total = impressions_yes + impressions_no
    pooled_rate = (clicks_yes + clicks_no) / total

    if pooled_rate <= 0 or pooled_rate >= 1:
        return 1.0

    se = np.sqrt(
        pooled_rate * (1 - pooled_rate)
        * (1 / impressions_yes + 1 / impressions_no)
    )
    if se == 0:
        return 1.0

    difference = clicks_yes / impressions_yes - clicks_no / impressions_no
    return float(2 * norm.sf(abs(difference / se)))


def benjamini_hochberg(p_values):
    p_values = np.asarray(p_values, dtype=float)
    n = len(p_values)
    order = np.argsort(p_values)
    sorted_p = p_values[order]

    adjusted_sorted = sorted_p * n / np.arange(1, n + 1)
    adjusted_sorted = np.minimum.accumulate(adjusted_sorted[::-1])[::-1]
    adjusted = np.empty(n)
    adjusted[order] = np.clip(adjusted_sorted, 0, 1)
    return adjusted


def main():
    comparison = pd.read_csv(COMPARISON_FILE)
    features = pd.read_parquet(FEATURE_FILE)
    balance = pd.read_parquet(BALANCE_FILE)

    flagged_ids = set(
        balance.loc[
            balance["balance_status"] == "Flag for exposure imbalance review",
            "experiment_id",
        ].astype(str)
    )

    comparison["experiment_id"] = comparison["experiment_id"].astype(str)
    features["clickability_test_id"] = features["clickability_test_id"].astype(str)

    original_experiments = set(comparison["experiment_id"].unique())
    excluded_ids = original_experiments & flagged_ids

    print("Experiments in original comparison:", len(original_experiments))
    print("Flagged experiments in balance file:", len(flagged_ids))
    print("Flagged experiments present in comparison:", len(excluded_ids))
    print("Excluded IDs:", sorted(excluded_ids))

    comparison = comparison[
        ~comparison["experiment_id"].isin(excluded_ids)
    ].copy()

    data = comparison.merge(
        features[["Unnamed: 0", "clickability_test_id", *FEATURES]],
        left_on="row_id",
        right_on="Unnamed: 0",
        how="left",
        validate="one_to_one",
    )

    if data[FEATURES].isna().any().any():
        raise ValueError("Missing headline features after join.")

    records = []

    for feature in FEATURES:
        for experiment_id, group in data.groupby("experiment_id", sort=False):
            present = group[group[feature].astype(bool)]
            absent = group[~group[feature].astype(bool)]

            if present.empty or absent.empty:
                continue

            cp, ip = int(present["clicks"].sum()), int(present["impressions"].sum())
            ca, ia = int(absent["clicks"].sum()), int(absent["impressions"].sum())

            records.append({
                "feature": feature,
                "experiment_id": experiment_id,
                "ctr_difference_pp": (cp / ip - ca / ia) * 100,
                "p_value": two_proportion_pvalue(cp, ip, ca, ia),
            })

    tests = pd.DataFrame(records)
    if tests.empty:
        raise ValueError("No valid experiment-feature tests remain.")

    # BH correction across the full sensitivity test family.
    tests["bh_adjusted_p_value"] = benjamini_hochberg(tests["p_value"])
    tests["bh_significant_05"] = tests["bh_adjusted_p_value"] < 0.05

    rng = np.random.default_rng(RANDOM_SEED)
    summaries = []

    for feature, group in tests.groupby("feature", sort=False):
        effects = group["ctr_difference_pp"].to_numpy()
        n = len(effects)
        boot = np.empty(BOOTSTRAP_REPS)

        for start in range(0, BOOTSTRAP_REPS, 500):
            size = min(500, BOOTSTRAP_REPS - start)
            sample = rng.choice(effects, size=(size, n), replace=True)
            boot[start:start + size] = sample.mean(axis=1)

        low, high = np.percentile(boot, [2.5, 97.5])

        summaries.append({
            "feature": feature,
            "experiments_tested": n,
            "mean_ctr_difference_pp": effects.mean(),
            "bootstrap_95ci_low_pp": low,
            "bootstrap_95ci_high_pp": high,
            "median_ctr_difference_pp": np.median(effects),
            "experiments_bh_significant_05": int(
                group["bh_significant_05"].sum()
            ),
        })

    summary = pd.DataFrame(summaries)
    tests.to_csv(TESTS_FILE, index=False)
    summary.to_csv(SUMMARY_FILE, index=False)

    print("\nSENSITIVITY SUMMARY")
    print(summary.round(4).to_string(index=False))
    print("\nSaved:", TESTS_FILE)
    print("Saved:", SUMMARY_FILE)


if __name__ == "__main__":
    main()