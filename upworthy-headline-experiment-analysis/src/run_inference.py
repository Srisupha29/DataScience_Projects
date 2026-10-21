
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

COMPARISON_FILE = PROCESSED / "eligible_headline_variant_comparisons.csv"
FEATURE_FILE = PROCESSED / "headline_features.parquet"

TESTS_FILE = PROCESSED / "phase23_within_experiment_tests.csv"
SUMMARY_FILE = PROCESSED / "phase23_feature_summary.csv"

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
    """Two-sided pooled two-proportion z-test."""
    total_impressions = impressions_yes + impressions_no
    pooled_rate = (clicks_yes + clicks_no) / total_impressions

    if pooled_rate <= 0 or pooled_rate >= 1:
        return 1.0

    standard_error = np.sqrt(
        pooled_rate
        * (1 - pooled_rate)
        * (1 / impressions_yes + 1 / impressions_no)
    )

    if standard_error == 0:
        return 1.0

    rate_difference = (
        clicks_yes / impressions_yes - clicks_no / impressions_no
    )
    z_score = rate_difference / standard_error

    return float(2 * norm.sf(abs(z_score)))


def benjamini_hochberg(p_values):
    """Return BH-adjusted p-values in their original order."""
    p_values = np.asarray(p_values, dtype=float)
    count = len(p_values)

    if count == 0:
        return np.array([])

    order = np.argsort(p_values)
    sorted_p = p_values[order]

    adjusted_sorted = sorted_p * count / np.arange(1, count + 1)
    adjusted_sorted = np.minimum.accumulate(adjusted_sorted[::-1])[::-1]
    adjusted_sorted = np.clip(adjusted_sorted, 0, 1)

    adjusted = np.empty(count)
    adjusted[order] = adjusted_sorted

    return adjusted


def main():
    comparison = pd.read_csv(COMPARISON_FILE)
    features = pd.read_parquet(FEATURE_FILE)

    required_comparison = {
        "row_id", "experiment_id", "impressions", "clicks"
    }
    required_features = {
        "Unnamed: 0", "clickability_test_id", *FEATURES
    }

    missing_comparison = required_comparison - set(comparison.columns)
    missing_features = required_features - set(features.columns)

    if missing_comparison or missing_features:
        raise ValueError(
            f"Missing comparison columns: {sorted(missing_comparison)}; "
            f"missing feature columns: {sorted(missing_features)}"
        )

    if comparison["row_id"].duplicated().any():
        raise ValueError("Comparison row_id is not unique.")

    if features["Unnamed: 0"].duplicated().any():
        raise ValueError("Feature index is not unique.")

    data = comparison.merge(
        features[["Unnamed: 0", "clickability_test_id", *FEATURES]],
        left_on="row_id",
        right_on="Unnamed: 0",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if not data["_merge"].eq("both").all():
        raise ValueError("Some comparison rows did not match feature rows.")

    if not data["experiment_id"].eq(data["clickability_test_id"]).all():
        raise ValueError("Experiment IDs do not match after joining.")

    if data[FEATURES].isna().any().any():
        raise ValueError("Missing values found in binary headline features.")

    if (data["impressions"] <= 0).any():
        raise ValueError("Non-positive impressions found.")

    if (
        (data["clicks"] < 0)
        | (data["clicks"] > data["impressions"])
    ).any():
        raise ValueError("Invalid clicks/impressions values found.")

    records = []

    for feature in FEATURES:
        for experiment_id, group in data.groupby("experiment_id", sort=False):
            present = group[group[feature].astype(bool)]
            absent = group[~group[feature].astype(bool)]

            # Compare only experiments containing both feature levels.
            if present.empty or absent.empty:
                continue

            clicks_present = int(present["clicks"].sum())
            impressions_present = int(present["impressions"].sum())
            clicks_absent = int(absent["clicks"].sum())
            impressions_absent = int(absent["impressions"].sum())

            rate_present = clicks_present / impressions_present
            rate_absent = clicks_absent / impressions_absent

            records.append({
                "feature": feature,
                "experiment_id": experiment_id,
                "arms_present": len(present),
                "arms_absent": len(absent),
                "clicks_present": clicks_present,
                "impressions_present": impressions_present,
                "clicks_absent": clicks_absent,
                "impressions_absent": impressions_absent,
                "ctr_present_pct": rate_present * 100,
                "ctr_absent_pct": rate_absent * 100,
                "ctr_difference_pp": (rate_present - rate_absent) * 100,
                "p_value": two_proportion_pvalue(
                    clicks_present,
                    impressions_present,
                    clicks_absent,
                    impressions_absent,
                ),
            })

    tests = pd.DataFrame(records)

    if tests.empty:
        raise ValueError("No valid within-experiment tests were found.")

    tests["bh_adjusted_p_value"] = benjamini_hochberg(tests["p_value"])
    tests["bh_significant_05"] = tests["bh_adjusted_p_value"] < 0.05

    # Bootstrap experiment-level effects, resampling experiments within feature.
    rng = np.random.default_rng(RANDOM_SEED)
    summaries = []

    for feature, group in tests.groupby("feature", sort=False):
        effects = group["ctr_difference_pp"].to_numpy()
        n_experiments = len(effects)

        bootstrap_means = np.empty(BOOTSTRAP_REPS)

        for start in range(0, BOOTSTRAP_REPS, 500):
            batch_size = min(500, BOOTSTRAP_REPS - start)
            sample = rng.choice(
                effects, size=(batch_size, n_experiments), replace=True
            )
            bootstrap_means[start:start + batch_size] = sample.mean(axis=1)

        ci_low, ci_high = np.percentile(bootstrap_means, [2.5, 97.5])

        summaries.append({
            "feature": feature,
            "experiments_tested": n_experiments,
            "mean_ctr_difference_pp": effects.mean(),
            "bootstrap_95ci_low_pp": ci_low,
            "bootstrap_95ci_high_pp": ci_high,
            "median_ctr_difference_pp": np.median(effects),
            "experiments_bh_significant_05": int(
                group["bh_significant_05"].sum()
            ),
        })

    summary = pd.DataFrame(summaries)

    tests.to_csv(TESTS_FILE, index=False)
    summary.to_csv(SUMMARY_FILE, index=False)

    print("\nVALIDATION")
    print("Joined comparison rows:", len(data))
    print("Experiments in comparison data:", data["experiment_id"].nunique())
    print("Valid experiment-feature tests:", len(tests))
    print("Features tested:", tests["feature"].nunique())

    print("\nFEATURE SUMMARY")
    print(summary.round(4).to_string(index=False))

    print("\nSaved:")
    print(TESTS_FILE)
    print(SUMMARY_FILE)


if __name__ == "__main__":
    main()
