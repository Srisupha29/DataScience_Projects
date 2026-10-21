
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]

PREDICTIONS_PATH = ROOT / "data/processed/phase24_oof_predictions.csv"
TARGETS_PATH = ROOT / "data/processed/phase24_modeling_targets.csv"
OUTPUT_PATH = ROOT / "data/processed/phase24_model_evaluation.csv"

MODEL_COLUMNS = {
    "Logistic Regression": "logistic_probability",
    "Gradient Boosting (Original)": "gradient_boosting_probability",
    "Gradient Boosting (Tuned)": "gradient_boosting_tuned_probability",
    "XGBoost": "xgboost_probability",
}

predictions = pd.read_csv(PREDICTIONS_PATH)
targets = pd.read_csv(TARGETS_PATH)

required_prediction_columns = {
    "row_id", "experiment_id", "target",
    *MODEL_COLUMNS.values(),
}
required_target_columns = {
    "row_id", "experiment_id", "relative_ctr",
}

if not required_prediction_columns.issubset(predictions.columns):
    raise ValueError(
        f"Missing prediction columns: "
        f"{required_prediction_columns - set(predictions.columns)}"
    )

if not required_target_columns.issubset(targets.columns):
    raise ValueError(
        f"Missing target columns: "
        f"{required_target_columns - set(targets.columns)}"
    )

data = predictions.merge(
    targets[["row_id", "experiment_id", "relative_ctr"]],
    on=["row_id", "experiment_id"],
    how="left",
    validate="one_to_one",
)

if data["relative_ctr"].isna().any():
    raise ValueError("Some predictions have no relative CTR.")
if len(data) != len(predictions):
    raise ValueError("The merge changed the prediction row count.")

results = []

for model_name, probability_column in MODEL_COLUMNS.items():
    probabilities = data[probability_column]

    if probabilities.isna().any():
        raise ValueError(f"Missing probabilities for {model_name}.")

    auc = roc_auc_score(data["target"], probabilities)

    experiment_scores = []
    correct_pairs = 0.0
    comparable_pairs = 0

    for experiment_id, group in data.groupby("experiment_id"):
        true_values = group["relative_ctr"].to_numpy()
        predicted_values = group[probability_column].to_numpy()

        experiment_correct = 0.0
        experiment_pairs = 0

        for i, j in combinations(range(len(group)), 2):
            true_difference = true_values[i] - true_values[j]

            # Ignore pairs with effectively tied observed relative CTR.
            if np.isclose(true_difference, 0.0, atol=1e-12):
                continue

            predicted_difference = predicted_values[i] - predicted_values[j]

            if np.isclose(predicted_difference, 0.0, atol=1e-12):
                score = 0.5
            elif np.sign(predicted_difference) == np.sign(true_difference):
                score = 1.0
            else:
                score = 0.0

            experiment_correct += score
            experiment_pairs += 1

        if experiment_pairs:
            experiment_scores.append(
                experiment_correct / experiment_pairs
            )
            correct_pairs += experiment_correct
            comparable_pairs += experiment_pairs

    results.append({
        "model": model_name,
        "roc_auc": auc,
        "mean_experiment_pairwise_accuracy": np.mean(
            experiment_scores
        ),
        "pooled_pairwise_accuracy": (
            correct_pairs / comparable_pairs
            if comparable_pairs else np.nan
        ),
        "experiments_evaluated": len(experiment_scores),
        "comparable_pairs": comparable_pairs,
    })

evaluation = pd.DataFrame(results)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
evaluation.to_csv(OUTPUT_PATH, index=False)

print("\nPHASE 2.4 MODEL EVALUATION")
print(evaluation.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
print(f"\nSaved: {OUTPUT_PATH}")
