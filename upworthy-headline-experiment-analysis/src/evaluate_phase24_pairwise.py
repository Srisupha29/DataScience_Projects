
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]

PAIRWISE_PATH = ROOT / "data/processed/phase24_pairwise_oof_predictions.csv"
POINTWISE_PATH = ROOT / "data/processed/phase24_oof_predictions.csv"
TARGET_PATH = ROOT / "data/processed/phase24_modeling_targets.csv"
OUTPUT_PATH = ROOT / "data/processed/phase24_pairwise_evaluation.csv"

# Keep evaluation ties out; separately assess clearly separated outcomes.
HIGH_GAP_THRESHOLD = 0.005
N_BOOTSTRAP = 2000
RANDOM_STATE = 42


def find_pointwise_score_column(frame):
    """Find the existing pointwise logistic-regression prediction column."""
    preferred = [
        "logistic_regression_probability",
        "logistic_probability",
        "logistic_regression_score",
        "logistic_score",
        "y_prob",
        "predicted_probability",
        "probability",
        "prediction",
        "score",
    ]

    lower_to_original = {c.lower(): c for c in frame.columns}

    for name in preferred:
        if name in lower_to_original:
            return lower_to_original[name]

    # Support wide-format OOF files with model names as column headers.
    candidates = [
        c for c in frame.columns
        if "logistic" in c.lower()
        and any(term in c.lower() for term in ["prob", "score", "pred"])
    ]
    if len(candidates) == 1:
        return candidates[0]

    # Do not accidentally treat identifiers or observed outcomes as scores.
    excluded = {
        "row_id", "experiment_id", "fold", "target",
        "relative_ctr", "clicks", "impressions", "ctr",
    }
    numeric = [
        c for c in frame.select_dtypes(include="number").columns
        if c.lower() not in excluded
    ]
    if len(numeric) == 1:
        return numeric[0]

    raise ValueError(
        "Could not identify the pointwise logistic prediction column. "
        f"Columns found: {frame.columns.tolist()}. "
        "Update find_pointwise_score_column() to match your OOF file."
    )


def load_predictions():
    pairwise = pd.read_csv(PAIRWISE_PATH)
    targets = pd.read_csv(TARGET_PATH)

    required_pairwise = {
        "row_id", "experiment_id", "relative_ctr", "pairwise_score"
    }
    if not required_pairwise.issubset(pairwise.columns):
        raise ValueError(
            f"Pairwise OOF file must contain {required_pairwise}."
        )

    # Attach the binary target for row-level ROC-AUC.
    target_columns = ["row_id", "experiment_id", "target"]
    if not set(target_columns).issubset(targets.columns):
        raise ValueError(
            "Modeling targets must contain row_id, experiment_id, target."
        )

    pairwise = pairwise.merge(
        targets[target_columns],
        on=["row_id", "experiment_id"],
        how="left",
        validate="one_to_one",
    )

    if pairwise["target"].isna().any():
        raise ValueError("Some pairwise predictions lack target labels.")

    pointwise_raw = pd.read_csv(POINTWISE_PATH)
    score_column = find_pointwise_score_column(pointwise_raw)

    pointwise = pointwise_raw[
        ["row_id", "experiment_id", score_column]
    ].rename(columns={score_column: "pointwise_score"})

    if pointwise["row_id"].duplicated().any():
        raise ValueError(
            "Pointwise OOF file has duplicate row IDs. "
            "If it stores multiple models in long format, filter it "
            "to Logistic Regression before evaluation."
        )

    data = pairwise.merge(
        pointwise,
        on=["row_id", "experiment_id"],
        how="left",
        validate="one_to_one",
    )

    if data["pointwise_score"].isna().any():
        raise ValueError(
            "Some rows have no matching pointwise predictions. "
            "Check the pointwise OOF file and row IDs."
        )

    return data


def experiment_pairwise_accuracies(data, score_column, high_gap_only):
    """
    Compute one accuracy per experiment, so large experiments do not
    automatically dominate the mean.
    """
    experiment_results = []

    for experiment_id, group in data.groupby("experiment_id", sort=False):
        ctr = group["relative_ctr"].to_numpy()
        scores = group[score_column].to_numpy()

        correct = []
        gaps = []

        for i, j in combinations(range(len(group)), 2):
            outcome_difference = ctr[i] - ctr[j]
            gap = abs(outcome_difference)

            # Exclude exact outcome ties from the all-pairs metric.
            if gap == 0:
                continue

            if high_gap_only and gap < HIGH_GAP_THRESHOLD:
                continue

            score_difference = scores[i] - scores[j]

            # Give a tied model score half credit.
            if score_difference == 0:
                pair_accuracy = 0.5
            else:
                pair_accuracy = float(
                    np.sign(score_difference)
                    == np.sign(outcome_difference)
                )

            correct.append(pair_accuracy)
            gaps.append(gap)

        if correct:
            experiment_results.append({
                "experiment_id": experiment_id,
                "accuracy": float(np.mean(correct)),
                "pairs": len(correct),
                "mean_gap": float(np.mean(gaps)),
            })

    return pd.DataFrame(experiment_results)


def bootstrap_ci(experiment_accuracies, rng):
    """Percentile bootstrap CI resampling experiments, not individual pairs."""
    values = np.asarray(experiment_accuracies, dtype=float)

    if len(values) == 0:
        return np.nan, np.nan

    boot_means = np.empty(N_BOOTSTRAP)

    for b in range(N_BOOTSTRAP):
        sample = rng.choice(values, size=len(values), replace=True)
        boot_means[b] = sample.mean()

    lower, upper = np.quantile(boot_means, [0.025, 0.975])
    return float(lower), float(upper)


def evaluate_model(data, model_name, score_column, subset_name,
                   high_gap_only, rng):
    experiment_results = experiment_pairwise_accuracies(
        data, score_column, high_gap_only
    )

    if experiment_results.empty:
        return {
            "model": model_name,
            "evaluation_subset": subset_name,
            "mean_experiment_pairwise_accuracy": np.nan,
            "ci_95_lower": np.nan,
            "ci_95_upper": np.nan,
            "experiments_evaluated": 0,
            "pairs_evaluated": 0,
            "roc_auc": np.nan,
        }

    lower, upper = bootstrap_ci(
        experiment_results["accuracy"].to_numpy(), rng
    )

    # ROC-AUC is row-level and is therefore reported on all rows only.
    auc = np.nan
    if subset_name == "All non-tied pairs":
        binary_target = data["target"].astype(int)
        if binary_target.nunique() == 2:
            auc = float(
                roc_auc_score(binary_target, data[score_column])
            )

    return {
        "model": model_name,
        "evaluation_subset": subset_name,
        "mean_experiment_pairwise_accuracy":
            float(experiment_results["accuracy"].mean()),
        "ci_95_lower": lower,
        "ci_95_upper": upper,
        "experiments_evaluated": len(experiment_results),
        "pairs_evaluated": int(experiment_results["pairs"].sum()),
        "roc_auc": auc,
    }


def main():
    data = load_predictions()
    rng = np.random.default_rng(RANDOM_STATE)

    models = [
        ("Weighted Pairwise Logistic Regression", "pairwise_score"),
        ("Pointwise Logistic Regression", "pointwise_score"),
    ]

    subsets = [
        ("All non-tied pairs", False),
        (f"High-gap pairs (gap >= {HIGH_GAP_THRESHOLD})", True),
    ]

    results = []

    for model_name, score_column in models:
        for subset_name, high_gap_only in subsets:
            results.append(
                evaluate_model(
                    data=data,
                    model_name=model_name,
                    score_column=score_column,
                    subset_name=subset_name,
                    high_gap_only=high_gap_only,
                    rng=rng,
                )
            )

    results = pd.DataFrame(results)
    results.to_csv(OUTPUT_PATH, index=False)

    print("\nWEIGHTED PAIRWISE MODEL EVALUATION")
    print(results.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nHigh-gap threshold: {HIGH_GAP_THRESHOLD}")
    print(f"Bootstrap samples: {N_BOOTSTRAP}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
