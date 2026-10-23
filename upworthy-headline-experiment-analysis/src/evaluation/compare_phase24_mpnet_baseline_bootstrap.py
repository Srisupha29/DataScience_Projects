
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PREDICTIONS_FILE = (
    PROCESSED_DIR / "phase24_embedding_ensemble_mpnet_oof_predictions.csv"
)
OUTPUT_FILE = (
    PROCESSED_DIR / "phase24_mpnet_vs_baseline_bootstrap.csv"
)
EXPERIMENT_OUTPUT_FILE = (
    PROCESSED_DIR / "phase24_mpnet_vs_baseline_experiment_accuracy.csv"
)

MIN_CTR_DIFFERENCE = 0.0005
N_BOOTSTRAP = 10_000
RANDOM_STATE = 20261023

BASELINE_COLUMN = "pairwise_score"
FINAL_COLUMN = "embedding_pairwise_score"


def experiment_pairwise_accuracy(group, score_column):
    ctr = group["relative_ctr"].to_numpy(dtype=float)
    scores = group[score_column].to_numpy(dtype=float)

    correct = []

    for i, j in combinations(range(len(group)), 2):
        ctr_diff = ctr[i] - ctr[j]

        if abs(ctr_diff) < MIN_CTR_DIFFERENCE:
            continue

        score_diff = scores[i] - scores[j]

        if np.isclose(score_diff, 0.0, atol=1e-12):
            correct.append(0.5)
        else:
            correct.append(
                float(np.sign(ctr_diff) == np.sign(score_diff))
            )

    if not correct:
        return np.nan, 0

    return float(np.mean(correct)), len(correct)


def main():
    if not PREDICTIONS_FILE.exists():
        raise FileNotFoundError(PREDICTIONS_FILE)

    df = pd.read_csv(PREDICTIONS_FILE)

    required = {
        "row_id",
        "experiment_id",
        "relative_ctr",
        BASELINE_COLUMN,
        FINAL_COLUMN,
    }
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df["row_id"].duplicated().any():
        raise ValueError("Duplicate row IDs detected.")

    for column in [BASELINE_COLUMN, FINAL_COLUMN, "relative_ctr"]:
        if not np.isfinite(df[column].to_numpy(dtype=float)).all():
            raise ValueError(f"Non-finite values found in {column}.")

    experiment_results = []

    for experiment_id, group in df.groupby("experiment_id", sort=False):
        baseline_acc, pair_count = experiment_pairwise_accuracy(
            group, BASELINE_COLUMN
        )
        final_acc, final_pair_count = experiment_pairwise_accuracy(
            group, FINAL_COLUMN
        )

        if pair_count != final_pair_count:
            raise ValueError(
                f"Comparable-pair mismatch in experiment {experiment_id}."
            )

        # Exclude experiments with no comparable pairs from both models.
        if np.isnan(baseline_acc) or np.isnan(final_acc):
            continue

        experiment_results.append({
            "experiment_id": experiment_id,
            "baseline_accuracy": baseline_acc,
            "mpnet_accuracy": final_acc,
            "accuracy_difference": final_acc - baseline_acc,
            "comparable_pairs": pair_count,
        })

    results = pd.DataFrame(experiment_results)

    if results.empty:
        raise ValueError("No experiments with comparable pairs were found.")

    results.to_csv(EXPERIMENT_OUTPUT_FILE, index=False)

    # Each experiment receives equal weight, matching mean
    # experiment-level pairwise accuracy.
    differences = results["accuracy_difference"].to_numpy(dtype=float)
    observed_difference = float(np.mean(differences))

    rng = np.random.default_rng(RANDOM_STATE)
    n = len(differences)
    bootstrap_differences = np.empty(N_BOOTSTRAP)

    for b in range(N_BOOTSTRAP):
        indices = rng.integers(0, n, size=n)
        bootstrap_differences[b] = np.mean(differences[indices])

    ci_low, ci_high = np.percentile(
        bootstrap_differences, [2.5, 97.5]
    )

    # Approximate two-sided bootstrap tail estimate.
    centered = bootstrap_differences - observed_difference
    tail_probability = np.mean(
        np.abs(centered) >= abs(observed_difference)
    )
    bootstrap_p_value = min(1.0, float(tail_probability))

    baseline_mean = float(results["baseline_accuracy"].mean())
    mpnet_mean = float(results["mpnet_accuracy"].mean())

    summary = pd.DataFrame([{
        "baseline_pairwise_accuracy": baseline_mean,
        "mpnet_pairwise_accuracy": mpnet_mean,
        "accuracy_gain": observed_difference,
        "ci_95_lower": float(ci_low),
        "ci_95_upper": float(ci_high),
        "bootstrap_p_value_approx": bootstrap_p_value,
        "experiments_evaluated": n,
        "comparable_pairs": int(results["comparable_pairs"].sum()),
        "bootstrap_resamples": N_BOOTSTRAP,
        "random_seed": RANDOM_STATE,
        "ci_excludes_zero": bool(ci_low > 0 or ci_high < 0),
    }])

    summary.to_csv(OUTPUT_FILE, index=False)

    print("FINAL MODEL VS BASELINE — PAIRED BOOTSTRAP")
    print(f"Experiments evaluated: {n:,}")
    print(
        f"Comparable pairs:      "
        f"{int(results['comparable_pairs'].sum()):,}"
    )
    print(f"Bootstrap resamples:   {N_BOOTSTRAP:,}")
    print(f"Random seed:           {RANDOM_STATE}")
    print()
    print(f"Baseline accuracy:     {baseline_mean:.4%}")
    print(f"MPNet accuracy:        {mpnet_mean:.4%}")
    print(f"Accuracy gain:         {observed_difference:+.4%}")
    print(f"95% bootstrap CI:      [{ci_low:+.4%}, {ci_high:+.4%}]")
    print(f"Approx. bootstrap p:   {bootstrap_p_value:.4f}")
    print(
        "95% CI excludes zero: "
        f"{'YES' if ci_low > 0 or ci_high < 0 else 'NO'}"
    )
    print(f"\nSaved summary: {OUTPUT_FILE}")
    print(f"Saved experiment results: {EXPERIMENT_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
