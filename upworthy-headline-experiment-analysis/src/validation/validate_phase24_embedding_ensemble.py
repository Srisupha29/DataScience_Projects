from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TARGETS_FILE = PROCESSED_DIR / "phase24_modeling_targets.csv"
FOLDS_FILE = PROCESSED_DIR / "phase24_cv_folds.csv"
BASELINE_FILE = PROCESSED_DIR / "phase24_pairwise_oof_predictions.csv"
OUTPUT_FILE = (
    PROCESSED_DIR / "phase24_embedding_ensemble_oof_predictions.csv"
)
REPORT_FILE = (
    PROCESSED_DIR / "phase24_embedding_ensemble_metrics.csv"
)

MIN_CTR_DIFFERENCE = 0.0005

SCORE_COLUMNS = {
    "Baseline pairwise": "pairwise_score",
    "Embedding pairwise": "embedding_pairwise_score",
    "XGBoost ranker": "xgb_rank_score",
    "Ensemble": "ensemble_score",
}


def mean_experiment_pairwise_accuracy(frame, score_column):
    """Calculate mean pairwise accuracy across experiments."""
    experiment_accuracies = []
    comparable_pairs = 0

    for _, group in frame.groupby("experiment_id", sort=False):
        ctr = group["relative_ctr"].to_numpy(dtype=float)
        scores = group[score_column].to_numpy(dtype=float)

        correct = []
        for i, j in combinations(range(len(group)), 2):
            ctr_difference = ctr[i] - ctr[j]

            if abs(ctr_difference) < MIN_CTR_DIFFERENCE:
                continue

            score_difference = scores[i] - scores[j]

            if np.isclose(score_difference, 0.0, atol=1e-12):
                correct.append(0.5)
            else:
                correct.append(
                    float(np.sign(ctr_difference) == np.sign(score_difference))
                )

        if correct:
            experiment_accuracies.append(np.mean(correct))
            comparable_pairs += len(correct)

    if not experiment_accuracies:
        raise ValueError("No comparable headline pairs found.")

    return (
        float(np.mean(experiment_accuracies)),
        len(experiment_accuracies),
        comparable_pairs,
    )


def main():
    for path in [TARGETS_FILE, FOLDS_FILE, BASELINE_FILE, OUTPUT_FILE]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    targets = pd.read_csv(TARGETS_FILE)
    folds = pd.read_csv(FOLDS_FILE)
    baseline = pd.read_csv(BASELINE_FILE)
    predictions = pd.read_csv(OUTPUT_FILE)

    # Normalize join keys before validation.
    for frame in [targets, folds, baseline, predictions]:
        frame["row_id"] = frame["row_id"].astype(str)

    if targets["row_id"].duplicated().any():
        raise ValueError("Targets contain duplicate row IDs.")

    if folds["row_id"].duplicated().any():
        raise ValueError("Fold assignments contain duplicate row IDs.")

    if predictions["row_id"].duplicated().any():
        raise ValueError("OOF predictions contain duplicate row IDs.")

    if baseline["row_id"].duplicated().any():
        raise ValueError("Baseline predictions contain duplicate row IDs.")

    expected_ids = set(targets["row_id"])
    output_ids = set(predictions["row_id"])

    if expected_ids != output_ids:
        raise ValueError(
            f"Prediction row coverage mismatch: "
            f"{len(expected_ids - output_ids)} missing, "
            f"{len(output_ids - expected_ids)} unexpected."
        )

    # Check target metadata against the output.
    target_meta = targets[
        ["row_id", "experiment_id", "relative_ctr"]
    ].copy()
    target_meta["experiment_id"] = target_meta["experiment_id"].astype(str)

    predictions["experiment_id"] = predictions["experiment_id"].astype(str)

    check = predictions[
        ["row_id", "experiment_id", "relative_ctr", "fold"]
    ].merge(
        target_meta,
        on="row_id",
        how="left",
        suffixes=("_output", "_target"),
        validate="one_to_one",
    )

    if not (
        check["experiment_id_output"] == check["experiment_id_target"]
    ).all():
        raise ValueError("Output experiment IDs do not match the targets.")

    if not np.allclose(
        check["relative_ctr_output"],
        check["relative_ctr_target"],
        rtol=1e-9,
        atol=1e-12,
    ):
        raise ValueError("Output relative_ctr values differ from the targets.")

    # Validate that the output uses the original fold assignments.
    fold_meta = folds[["row_id", "fold"]].copy()
    fold_meta["fold"] = fold_meta["fold"].astype(int)

    fold_check = predictions[["row_id", "fold"]].merge(
        fold_meta,
        on="row_id",
        how="left",
        suffixes=("_output", "_source"),
        validate="one_to_one",
    )

    if fold_check["fold_source"].isna().any():
        raise ValueError("Some output rows have no source fold assignment.")

    if not (
        fold_check["fold_output"].astype(int)
        == fold_check["fold_source"].astype(int)
    ).all():
        raise ValueError("Output fold assignments differ from the source.")

    # Every experiment must remain entirely within one fold.
    folds_per_experiment = predictions.groupby("experiment_id")["fold"].nunique()

    if (folds_per_experiment != 1).any():
        raise ValueError("At least one experiment appears in multiple folds.")

    # Ensure baseline scores were preserved.
    baseline_check = predictions[["row_id", "pairwise_score"]].merge(
        baseline[["row_id", "pairwise_score"]],
        on="row_id",
        how="left",
        suffixes=("_output", "_source"),
        validate="one_to_one",
    )

    if baseline_check["pairwise_score_source"].isna().any():
        raise ValueError("Some baseline scores are missing.")

    if not np.allclose(
        baseline_check["pairwise_score_output"],
        baseline_check["pairwise_score_source"],
        rtol=1e-9,
        atol=1e-12,
    ):
        raise ValueError("Baseline predictions were changed.")

    # Validate all prediction columns.
    for name, column in SCORE_COLUMNS.items():
        if column not in predictions.columns:
            raise ValueError(f"Missing score column for {name}: {column}")

        scores = predictions[column].to_numpy(dtype=float)
        if not np.isfinite(scores).all():
            raise ValueError(f"{name} contains missing or non-finite scores.")

    # Recompute target from the documented definition.
    y_true = (predictions["relative_ctr"].to_numpy() > 0).astype(int)

    results = []
    for name, column in SCORE_COLUMNS.items():
        auc = roc_auc_score(y_true, predictions[column])

        mean_accuracy, evaluated_experiments, pair_count = (
            mean_experiment_pairwise_accuracy(predictions, column)
        )

        results.append({
            "model": name,
            "roc_auc": auc,
            "mean_experiment_pairwise_accuracy": mean_accuracy,
            "experiments_evaluated": evaluated_experiments,
            "comparable_pairs": pair_count,
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(REPORT_FILE, index=False)

    print("PREDICTION VALIDATION PASSED")
    print(f"Rows: {len(predictions):,}")
    print(f"Experiments: {predictions['experiment_id'].nunique():,}")
    print(f"Folds: {predictions['fold'].nunique()}")
    print("Experiment grouping: valid")
    print("Fold assignments: unchanged")
    print("Baseline predictions: unchanged")
    print("Missing or non-finite scores: none")

    print("\nMODEL COMPARISON")
    print(
        results_df.to_string(
            index=False,
            formatters={
                "roc_auc": "{:.4f}".format,
                "mean_experiment_pairwise_accuracy": "{:.4%}".format,
            },
        )
    )

    print(f"\nSaved metrics: {REPORT_FILE}")
    print("Evaluation remains open; no final conclusion is made.")


if __name__ == "__main__":
    main()