
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data/processed/phase24_modeling_features.csv"
OUTPUT_PATH = ROOT / "data/processed/phase24_cv_folds.csv"

N_SPLITS = 5
RANDOM_STATE = 42

data = pd.read_csv(INPUT_PATH)

required = {"row_id", "experiment_id", "target"}
missing = required - set(data.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

if data["row_id"].duplicated().any():
    raise ValueError("row_id must be unique.")

if data[["experiment_id", "target"]].isna().any().any():
    raise ValueError("Missing experiment IDs or target labels.")

splitter = StratifiedGroupKFold(
    n_splits=N_SPLITS,
    shuffle=True,
    random_state=RANDOM_STATE,
)

fold_assignments = pd.Series(index=data.index, dtype="int64")

for fold, (_, validation_idx) in enumerate(
    splitter.split(
        X=data[["row_id"]],
        y=data["target"],
        groups=data["experiment_id"],
    ),
    start=1,
):
    fold_assignments.iloc[validation_idx] = fold

if fold_assignments.isna().any():
    raise ValueError("Some rows were not assigned a validation fold.")

data["fold"] = fold_assignments.astype("int8")

# Every experiment must belong to exactly one validation fold.
folds_per_experiment = data.groupby("experiment_id")["fold"].nunique()
if not folds_per_experiment.eq(1).all():
    raise ValueError("An experiment appears in multiple validation folds.")

if data["row_id"].nunique() != len(data):
    raise ValueError("Duplicate rows detected.")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
data[["row_id", "experiment_id", "target", "fold"]].to_csv(
    OUTPUT_PATH, index=False
)

print("GROUPED CROSS-VALIDATION VALIDATION")
print(f"Rows: {len(data):,}")
print(f"Experiments: {data['experiment_id'].nunique():,}")
print(f"Folds: {N_SPLITS}")
print(
    "Experiments assigned to exactly one fold:",
    int(folds_per_experiment.eq(1).sum()),
)
print("\nFold summary:")
print(
    data.groupby("fold").agg(
        rows=("row_id", "size"),
        experiments=("experiment_id", "nunique"),
        positives=("target", "sum"),
        positive_rate=("target", "mean"),
    ).round(4).to_string()
)
print(f"\nSaved: {OUTPUT_PATH}")
