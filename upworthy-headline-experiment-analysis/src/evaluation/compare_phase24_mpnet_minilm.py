
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MINILM_FILE = (
    PROCESSED_DIR / "phase24_embedding_ensemble_oof_predictions.csv"
)
MPNET_FILE = (
    PROCESSED_DIR / "phase24_embedding_ensemble_mpnet_oof_predictions.csv"
)
OUTPUT_FILE = (
    PROCESSED_DIR / "phase24_mpnet_vs_minilm_comparison.csv"
)

MIN_CTR_DIFFERENCE = 0.0005
STOPPING_THRESHOLD = 0.005

SCORE_COLUMNS = {
    "Embedding pairwise": "embedding_pairwise_score",
    "Ensemble": "ensemble_score",
}


def load_predictions(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    required = {
        "row_id",
        "experiment_id",
        "fold",
        "relative_ctr",
        *SCORE_COLUMNS.values(),
    }
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")

    df["row_id"] = df["row_id"].astype(str)
    df["experiment_id"] = df["experiment_id"].astype(str)

    if df["row_id"].duplicated().any():
        raise ValueError(f"{path.name} contains duplicate row IDs.")

    for column in SCORE_COLUMNS.values():
        if not np.isfinite(df[column].to_numpy(dtype=float)).all():
            raise ValueError(f"{path.name}: invalid values in {column}")

    return df


def mean_experiment_pairwise_accuracy(df, score_column):
    experiment_accuracies = []
    comparable_pairs = 0

    for _, group in df.groupby("experiment_id", sort=False):
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

        if correct:
            experiment_accuracies.append(float(np.mean(correct)))
            comparable_pairs += len(correct)

    if not experiment_accuracies:
        raise ValueError("No comparable experiment pairs were found.")

    return (
        float(np.mean(experiment_accuracies)),
        len(experiment_accuracies),
        comparable_pairs,
    )


def main():
    minilm = load_predictions(MINILM_FILE)
    mpnet = load_predictions(MPNET_FILE)

    # Align rows explicitly; never compare based on incidental row order.
    if set(minilm["row_id"]) != set(mpnet["row_id"]):
        raise ValueError("MiniLM and MPNet have different row ID coverage.")

    keys = ["row_id", "experiment_id", "fold", "relative_ctr"]

    aligned = minilm[keys].merge(
        mpnet[keys],
        on="row_id",
        how="inner",
        suffixes=("_minilm", "_mpnet"),
        validate="one_to_one",
    )

    for column in ["experiment_id", "fold", "relative_ctr"]:
        left = aligned[f"{column}_minilm"]
        right = aligned[f"{column}_mpnet"]

        if column == "relative_ctr":
            same = np.allclose(
                left.to_numpy(dtype=float),
                right.to_numpy(dtype=float),
                rtol=1e-9,
                atol=1e-12,
            )
        else:
            same = (left.astype(str).to_numpy() ==
                    right.astype(str).to_numpy()).all()

        if not same:
            raise ValueError(f"Mismatch between runs in {column}.")

    results = []

    for model_name, score_column in SCORE_COLUMNS.items():
        for run_name, predictions in [
            ("MiniLM", minilm),
            ("MPNet", mpnet),
        ]:
            y_true = (predictions["relative_ctr"].to_numpy() > 0).astype(int)
            auc = roc_auc_score(y_true, predictions[score_column])

            accuracy, experiments, pairs = (
                mean_experiment_pairwise_accuracy(predictions, score_column)
            )

            results.append({
                "model": model_name,
                "embedding": run_name,
                "roc_auc": auc,
                "pairwise_accuracy": accuracy,
                "experiments_evaluated": experiments,
                "comparable_pairs": pairs,
            })

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_FILE, index=False)

    print("MPNET VS MINILM — CONTROLLED COMPARISON")
    print("---------------------------------------")
    print(f"Matched rows: {len(aligned):,}")
    print(f"Experiments: {minilm['experiment_id'].nunique():,}")
    print(f"Fold assignments and targets: matched")

    for model_name in SCORE_COLUMNS:
        subset = results_df[results_df["model"] == model_name].set_index(
            "embedding"
        )

        minilm_acc = subset.loc["MiniLM", "pairwise_accuracy"]
        mpnet_acc = subset.loc["MPNet", "pairwise_accuracy"]
        minilm_auc = subset.loc["MiniLM", "roc_auc"]
        mpnet_auc = subset.loc["MPNet", "roc_auc"]

        delta_pp = (mpnet_acc - minilm_acc) * 100
        delta_auc = mpnet_auc - minilm_auc

        print(f"\n{model_name}")
        print(f"  MiniLM pairwise accuracy: {minilm_acc:.4%}")
        print(f"  MPNet pairwise accuracy:  {mpnet_acc:.4%}")
        print(f"  Accuracy change:          {delta_pp:+.3f} percentage points")
        print(f"  MiniLM ROC-AUC:           {minilm_auc:.4f}")
        print(f"  MPNet ROC-AUC:            {mpnet_auc:.4f}")
        print(f"  ROC-AUC change:            {delta_auc:+.4f}")

        if model_name == "Embedding pairwise":
            if delta_pp < STOPPING_THRESHOLD * 100:
                print(
                    "  Stopping rule: gain is below 0.5 percentage points; "
                    "stop testing larger embedding models."
                )
            else:
                print(
                    "  Stopping rule: gain meets or exceeds 0.5 percentage "
                    "points; assess whether further testing is justified."
                )

    print(f"\nSaved comparison: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
