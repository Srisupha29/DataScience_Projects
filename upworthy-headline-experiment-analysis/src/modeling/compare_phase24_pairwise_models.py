
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TARGETS_FILE = PROCESSED_DIR / "phase24_modeling_targets.csv"
PAIRWISE_FILE = PROCESSED_DIR / "phase24_pairwise_oof_predictions.csv"
POINTWISE_FILE = PROCESSED_DIR / "phase24_oof_predictions.csv"

OUTPUT_FILE = PROCESSED_DIR / "phase24_paired_bootstrap_comparison.csv"

N_BOOTSTRAPS = 2_000
RANDOM_STATE = 42

# Relative CTR differences equal to zero are excluded.
# This matches the previous all-non-tied-pairs evaluation.

def find_column(df, candidates, description):
    """Return the first matching column name or raise a useful error."""
    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        f"Could not identify {description}.\n"
        f"Available columns: {df.columns.tolist()}\n"
        f"Expected one of: {candidates}"
    )


def pairwise_accuracy_for_experiment(group, score_column):
    """
    Compute within-experiment pairwise accuracy.

    Each non-tied pair contributes:
      1.0 if the model ranks the higher-relative-CTR headline higher
      0.0 if it ranks the pair incorrectly
      0.5 if the model gives both headlines equal scores
    """
    relative_ctr = group["relative_ctr"].to_numpy(dtype=float)
    scores = group[score_column].to_numpy(dtype=float)

    valid = np.isfinite(relative_ctr) & np.isfinite(scores)
    relative_ctr = relative_ctr[valid]
    scores = scores[valid]

    n = len(relative_ctr)
    if n < 2:
        return np.nan, 0

    i, j = np.triu_indices(n, k=1)

    actual_difference = relative_ctr[i] - relative_ctr[j]
    predicted_difference = scores[i] - scores[j]

    # Exclude actual CTR ties, consistent with the previous evaluation.
    non_tied = actual_difference != 0
    actual_difference = actual_difference[non_tied]
    predicted_difference = predicted_difference[non_tied]

    if len(actual_difference) == 0:
        return np.nan, 0

    correct = np.where(
        predicted_difference == 0,
        0.5,
        (np.sign(actual_difference) == np.sign(predicted_difference)).astype(float),
    )

    return float(correct.mean()), int(len(correct))


def main():
    # -----------------------------------------------------
    # 1. Load the three existing out-of-fold datasets
    # -----------------------------------------------------
    targets = pd.read_csv(TARGETS_FILE)
    pairwise = pd.read_csv(PAIRWISE_FILE)
    pointwise = pd.read_csv(POINTWISE_FILE)

    print("TARGET COLUMNS")
    print(targets.columns.tolist())
    print("\nPAIRWISE PREDICTION COLUMNS")
    print(pairwise.columns.tolist())
    print("\nPOINTWISE PREDICTION COLUMNS")
    print(pointwise.columns.tolist())

    row_id_col = find_column(
        targets, ["row_id"], "target row ID"
    )
    experiment_col = find_column(
        targets, ["experiment_id"], "experiment ID"
    )
    ctr_col = find_column(
        targets,
        ["relative_ctr", "relative_CTR", "ctr_difference"],
        "relative CTR target",
    )

    pairwise_row_id = find_column(
        pairwise, ["row_id"], "pairwise row ID"
    )
    pairwise_score_col = find_column(
        pairwise,
        [
            "pairwise_score",
            "weighted_pairwise_score",
            "pairwise_utility",
            "weighted_pairwise_utility",
            "score",
            "utility",
        ],
        "weighted pairwise model score",
    )

    pointwise_row_id = find_column(
        pointwise, ["row_id"], "pointwise row ID"
    )
    pointwise_score_col = find_column(
        pointwise,
        ["logistic_probability"],
        "pointwise logistic probability",
    )

    # Keep only the required columns to prevent duplicate-column
    # problems during merges.
    target_data = targets[
        [row_id_col, experiment_col, ctr_col]
    ].rename(
        columns={
            row_id_col: "row_id",
            experiment_col: "experiment_id",
            ctr_col: "relative_ctr",
        }
    )

    pairwise_data = pairwise[
        [pairwise_row_id, pairwise_score_col]
    ].rename(
        columns={
            pairwise_row_id: "row_id",
            pairwise_score_col: "pairwise_score",
        }
    )

    pointwise_data = pointwise[
        [pointwise_row_id, pointwise_score_col]
    ].rename(
        columns={
            pointwise_row_id: "row_id",
            pointwise_score_col: "pointwise_score",
        }
    )

    # Each source should contain one prediction per row.
    for name, data in [
        ("targets", target_data),
        ("pairwise predictions", pairwise_data),
        ("pointwise predictions", pointwise_data),
    ]:
        if data["row_id"].duplicated().any():
            raise ValueError(
                f"{name} contains duplicate row_id values."
            )

    # -----------------------------------------------------
    # 2. Align both models on exactly the same observations
    # -----------------------------------------------------
    merged = (
        target_data
        .merge(pairwise_data, on="row_id", how="inner", validate="one_to_one")
        .merge(pointwise_data, on="row_id", how="inner", validate="one_to_one")
    )

    if merged.empty:
        raise ValueError("No matching rows found across the three datasets.")

    if merged[["relative_ctr", "pairwise_score", "pointwise_score"]].isna().any().any():
        raise ValueError(
            "Missing relative CTR or model scores detected after merging. "
            "Investigate before comparing the models."
        )

    print("\nDATA ALIGNMENT")
    print(f"Target rows: {len(target_data):,}")
    print(f"Pairwise prediction rows: {len(pairwise_data):,}")
    print(f"Pointwise prediction rows: {len(pointwise_data):,}")
    print(f"Matched rows: {len(merged):,}")
    print(f"Experiments: {merged['experiment_id'].nunique():,}")

    # -----------------------------------------------------
    # 3. Compute both accuracies per experiment
    # -----------------------------------------------------
    records = []

    for experiment_id, group in merged.groupby("experiment_id", sort=False):
        pairwise_accuracy, pairwise_pairs = pairwise_accuracy_for_experiment(
            group, "pairwise_score"
        )
        pointwise_accuracy, pointwise_pairs = pairwise_accuracy_for_experiment(
            group, "pointwise_score"
        )

        # The pair sets should match because both models are scored
        # on the same rows and use the same actual relative CTR values.
        if pairwise_pairs != pointwise_pairs:
            raise ValueError(
                f"Pair count mismatch for experiment {experiment_id}."
            )

        if pairwise_pairs == 0:
            continue

        records.append(
            {
                "experiment_id": experiment_id,
                "pairwise_accuracy": pairwise_accuracy,
                "pointwise_accuracy": pointwise_accuracy,
                "accuracy_difference": pairwise_accuracy - pointwise_accuracy,
                "pairs_evaluated": pairwise_pairs,
            }
        )

    experiment_results = pd.DataFrame(records)

    if experiment_results.empty:
        raise ValueError("No experiments had evaluable non-tied pairs.")

    # Paired difference: both models are compared within each experiment.
    differences = experiment_results["accuracy_difference"].to_numpy()
    observed_gap = float(differences.mean())

    # -----------------------------------------------------
    # 4. Paired bootstrap over experiment IDs
    # -----------------------------------------------------
    rng = np.random.default_rng(RANDOM_STATE)
    n_experiments = len(differences)

    bootstrap_gaps = np.empty(N_BOOTSTRAPS)

    for b in range(N_BOOTSTRAPS):
        sampled_indices = rng.integers(
            low=0,
            high=n_experiments,
            size=n_experiments,
        )
        bootstrap_gaps[b] = differences[sampled_indices].mean()

    ci_lower, ci_upper = np.percentile(bootstrap_gaps, [2.5, 97.5])

    statistically_significant = (ci_lower > 0) or (ci_upper < 0)

    # Two-sided bootstrap tail estimate around zero.
    # Report as a descriptive bootstrap estimate, not an exact test p-value.
    p_bootstrap = min(
        1.0,
        2 * min(
            np.mean(bootstrap_gaps <= 0),
            np.mean(bootstrap_gaps >= 0),
        ),
    )

    # -----------------------------------------------------
    # 5. Save and report results
    # -----------------------------------------------------
    summary = pd.DataFrame(
        [
            {
                "comparison": "Weighted pairwise minus pointwise logistic",
                "pairwise_mean_experiment_accuracy": experiment_results[
                    "pairwise_accuracy"
                ].mean(),
                "pointwise_mean_experiment_accuracy": experiment_results[
                    "pointwise_accuracy"
                ].mean(),
                "mean_accuracy_difference": observed_gap,
                "ci_95_lower": float(ci_lower),
                "ci_95_upper": float(ci_upper),
                "bootstrap_tail_estimate": float(p_bootstrap),
                "experiments_evaluated": n_experiments,
                "pairs_evaluated": int(experiment_results["pairs_evaluated"].sum()),
                "bootstrap_draws": N_BOOTSTRAPS,
                "statistically_significant_at_5pct": statistically_significant,
            }
        ]
    )

    summary.to_csv(OUTPUT_FILE, index=False)

    print("\nPAIRED BOOTSTRAP COMPARISON")
    print(f"Pairwise mean experiment accuracy: "
          f"{experiment_results['pairwise_accuracy'].mean():.4%}")
    print(f"Pointwise mean experiment accuracy: "
          f"{experiment_results['pointwise_accuracy'].mean():.4%}")
    print(f"Mean accuracy gap: {observed_gap:+.4%}")
    print(f"95% bootstrap CI: [{ci_lower:+.4%}, {ci_upper:+.4%}]")
    print(f"Bootstrap tail estimate: {p_bootstrap:.4f}")
    print(f"Experiments evaluated: {n_experiments:,}")
    print(f"Pairs evaluated: {experiment_results['pairs_evaluated'].sum():,}")
    print(f"Bootstrap draws: {N_BOOTSTRAPS:,}")
    print(
        "Significant at 5% based on CI: "
        f"{'YES' if statistically_significant else 'NO'}"
    )
    print(f"\nSaved summary: {OUTPUT_FILE}")

    # Save per-experiment differences too, so the comparison is auditable.
    experiment_output = (
        PROCESSED_DIR / "phase24_paired_bootstrap_experiment_results.csv"
    )
    experiment_results.to_csv(experiment_output, index=False)
    print(f"Saved per-experiment results: {experiment_output}")


if __name__ == "__main__":
    main()
