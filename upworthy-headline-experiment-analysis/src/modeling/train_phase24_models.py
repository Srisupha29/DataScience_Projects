
from pathlib import Path

import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]

FEATURE_PATH = ROOT / "data/processed/phase24_modeling_features.csv"
FOLD_PATH = ROOT / "data/processed/phase24_cv_folds.csv"
OUTPUT_PATH = ROOT / "data/processed/phase24_oof_predictions.csv"

BINARY_FEATURES = [
    "contains_question_mark",
    "contains_exclamation_mark",
    "contains_number",
    "contains_you_family",
    "contains_first_person_pronoun",
    "contains_third_person_pronoun",
]

data = pd.read_csv(FEATURE_PATH)
folds = pd.read_csv(FOLD_PATH)

data = data.merge(
    folds[["row_id", "experiment_id", "fold"]],
    on=["row_id", "experiment_id"],
    how="left",
    validate="one_to_one",
)

if data["fold"].isna().any():
    raise ValueError("Some rows have no cross-validation fold.")
if data["target"].isna().any():
    raise ValueError("Missing target labels.")
if data["row_id"].duplicated().any():
    raise ValueError("Duplicate row IDs detected.")

X_text = data["headline"].fillna("").astype(str)
X_binary = data[BINARY_FEATURES].astype("int8").to_numpy()
y = data["target"].astype("int8").to_numpy()
fold_ids = data["fold"].to_numpy()

model_columns = {
    "logistic_probability": lambda: LogisticRegression(
        max_iter=2000,
        random_state=42,
    ),
    "gradient_boosting_probability": lambda: GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        max_features="sqrt",
        subsample=0.8,
        random_state=42,
    ),
    "gradient_boosting_tuned_probability": lambda: GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.03,
        max_depth=1,
        max_features="sqrt",
        subsample=0.8,
        min_samples_leaf=10,
        random_state=42,
    ),
    "xgboost_probability": lambda: XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=300,
        learning_rate=0.05,
        max_depth=3,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.5,
        reg_lambda=5.0,
        reg_alpha=0.1,
        tree_method="hist",
        n_jobs=2,
        random_state=42,
    ),
}

predictions = data[
    ["row_id", "experiment_id", "target", "fold"]
].copy()

for column in model_columns:
    predictions[column] = float("nan")

for fold in sorted(data["fold"].unique()):
    train_idx = fold_ids != fold
    valid_idx = fold_ids == fold

    # Fit vocabulary on training rows only.
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=5000,
        sublinear_tf=True,
    )

    X_train_text = vectorizer.fit_transform(X_text[train_idx])
    X_valid_text = vectorizer.transform(X_text[valid_idx])

    X_train = hstack(
        [X_train_text, csr_matrix(X_binary[train_idx])],
        format="csr",
    )
    X_valid = hstack(
        [X_valid_text, csr_matrix(X_binary[valid_idx])],
        format="csr",
    )

    for column, make_model in model_columns.items():
        model = make_model()
        model.fit(X_train, y[train_idx])

        predictions.loc[valid_idx, column] = (
            model.predict_proba(X_valid)[:, 1]
        )

        print(f"Fold {fold}: completed {column}")

    print(
        f"Fold {fold} complete: "
        f"training rows={train_idx.sum():,}, "
        f"validation rows={valid_idx.sum():,}, "
        f"vocabulary={len(vectorizer.vocabulary_):,}"
    )

if predictions[list(model_columns)].isna().any().any():
    raise ValueError("Some models have missing out-of-fold predictions.")

if len(predictions) != len(data):
    raise ValueError("Prediction row count changed.")

if predictions["row_id"].nunique() != len(predictions):
    raise ValueError("Duplicate prediction rows.")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
predictions.to_csv(OUTPUT_PATH, index=False)

print("\nMODEL TRAINING VALIDATION")
print(f"Rows: {len(predictions):,}")
print(f"Experiments: {predictions['experiment_id'].nunique():,}")
print(f"Folds: {predictions['fold'].nunique()}")
print("All four models produced out-of-fold predictions.")
print(f"Saved: {OUTPUT_PATH}")
