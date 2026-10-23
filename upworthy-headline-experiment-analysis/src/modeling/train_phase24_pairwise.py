
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]

FEATURE_PATH = ROOT / "data/processed/phase24_modeling_features.csv"
TARGET_PATH = ROOT / "data/processed/phase24_modeling_targets.csv"
FOLD_PATH = ROOT / "data/processed/phase24_cv_folds.csv"
OUTPUT_PATH = ROOT / "data/processed/phase24_pairwise_oof_predictions.csv"

MIN_CTR_DIFFERENCE = 0.0005

BINARY_FEATURES = [
    "contains_question_mark",
    "contains_exclamation_mark",
    "contains_number",
    "contains_you_family",
    "contains_first_person_pronoun",
    "contains_third_person_pronoun",
]


def load_data():
    data = pd.read_csv(FEATURE_PATH)
    targets = pd.read_csv(TARGET_PATH)
    folds = pd.read_csv(FOLD_PATH)

    data = data.drop(
        columns=[
            c for c in ["relative_ctr", "target", "fold"]
            if c in data.columns
        ]
    )

    data = data.merge(
        targets[["row_id", "experiment_id", "relative_ctr"]],
        on=["row_id", "experiment_id"],
        how="left",
        validate="one_to_one",
    )
    data = data.merge(
        folds[["row_id", "experiment_id", "fold"]],
        on=["row_id", "experiment_id"],
        how="left",
        validate="one_to_one",
    )

    if data["relative_ctr"].isna().any():
        raise ValueError("Missing relative CTR values.")
    if data["fold"].isna().any():
        raise ValueError("Missing fold assignments.")
    if data["row_id"].duplicated().any():
        raise ValueError("Duplicate row IDs.")
    if not set(BINARY_FEATURES).issubset(data.columns):
        raise ValueError("Required binary headline features are missing.")

    data["headline"] = data["headline"].fillna("").astype(str)
    data["fold"] = data["fold"].astype(int)
    return data


def build_numeric_features(data):
    text = data["headline"]
    words = text.str.findall(r"\b[\w']+\b")

    numeric = pd.DataFrame(index=data.index)
    numeric["char_count"] = text.str.len()
    numeric["word_count"] = words.str.len()
    numeric["avg_word_length"] = (
        numeric["char_count"] / numeric["word_count"].clip(lower=1)
    )
    numeric["question_count"] = text.str.count(r"\?")
    numeric["exclamation_count"] = text.str.count("!")
    numeric["comma_count"] = text.str.count(",")
    numeric["colon_semicolon_count"] = text.str.count(r"[:;]")
    numeric["uppercase_ratio"] = text.map(
        lambda s: sum(c.isupper() for c in s) / max(len(s), 1)
    )
    numeric["starts_with_number"] = (
        text.str.match(r"^\s*\d").astype(int)
    )
    numeric["second_person_count"] = text.str.lower().map(
        lambda s: sum(
            s.split().count(w)
            for w in ["you", "your", "yours", "yourself"]
        )
    )
    numeric["you_per_word"] = (
        numeric["second_person_count"]
        / numeric["word_count"].clip(lower=1)
    )

    binary = data[BINARY_FEATURES].fillna(0).astype(float)
    return pd.concat([numeric, binary], axis=1).astype(float)


def build_pairwise_training_data(train_rows, X_train):
    train_ctr = train_rows["relative_ctr"].to_numpy()

    pair_i, pair_j, pair_y, pair_weights = [], [], [], []

    # Group indices are positional within train_rows and X_train.
    for _, positions in train_rows.groupby(
        "experiment_id", sort=False
    ).indices.items():
        positions = np.asarray(positions, dtype=int)

        for i, j in combinations(positions, 2):
            difference = train_ctr[i] - train_ctr[j]
            gap = abs(difference)

            if gap < MIN_CTR_DIFFERENCE:
                continue

            label = int(difference > 0)

            # Original orientation.
            pair_i.append(i)
            pair_j.append(j)
            pair_y.append(label)
            pair_weights.append(gap)

            # Reverse orientation, with the opposite label.
            pair_i.append(j)
            pair_j.append(i)
            pair_y.append(1 - label)
            pair_weights.append(gap)

    if not pair_y:
        raise ValueError(
            "No training pairs remain after filtering near-ties."
        )

    pair_i = np.asarray(pair_i, dtype=int)
    pair_j = np.asarray(pair_j, dtype=int)
    y_pairs = np.asarray(pair_y, dtype=np.int8)
    sample_weights = np.asarray(pair_weights, dtype=float)

    if len(np.unique(y_pairs)) != 2:
        raise ValueError(
            f"Pairwise data has only one class: {np.unique(y_pairs)}"
        )

    # Mean weight 1 keeps the weight scale comparable across folds.
    sample_weights /= sample_weights.mean()

    X_pairs = X_train[pair_i] - X_train[pair_j]
    return X_pairs, y_pairs, sample_weights


def main():
    data = load_data()
    numeric = build_numeric_features(data)
    data["pairwise_score"] = np.nan

    for fold in sorted(data["fold"].unique()):
        train_mask = data["fold"].to_numpy() != fold
        valid_mask = ~train_mask

        train_rows = data.loc[train_mask].copy()
        valid_rows = data.loc[valid_mask].copy()

        if train_rows["experiment_id"].isin(
            valid_rows["experiment_id"]
        ).any():
            raise ValueError(f"Experiment leakage in fold {fold}.")

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=5,
            max_features=1000,
            sublinear_tf=True,
        )

        X_train_text = vectorizer.fit_transform(train_rows["headline"])
        X_valid_text = vectorizer.transform(valid_rows["headline"])

        scaler = StandardScaler()
        X_train_num = scaler.fit_transform(numeric.loc[train_mask])
        X_valid_num = scaler.transform(numeric.loc[valid_mask])

        X_train = hstack(
            [X_train_text, csr_matrix(X_train_num)], format="csr"
        )
        X_valid = hstack(
            [X_valid_text, csr_matrix(X_valid_num)], format="csr"
        )

        X_pairs, y_pairs, sample_weights = build_pairwise_training_data(
            train_rows, X_train
        )

        model = LogisticRegression(
            C=0.1,
            fit_intercept=False,
            max_iter=2000,
            random_state=42,
        )
        model.fit(X_pairs, y_pairs, sample_weight=sample_weights)

        scores = np.asarray(X_valid @ model.coef_.ravel()).ravel()
        data.loc[valid_mask, "pairwise_score"] = scores

        counts = np.bincount(y_pairs, minlength=2)
        print(
            f"Fold {fold}: "
            f"train headlines={int(train_mask.sum()):,}, "
            f"validation headlines={int(valid_mask.sum()):,}, "
            f"pairs={len(y_pairs):,}, "
            f"class counts={counts.tolist()}, "
            f"mean weight={sample_weights.mean():.3f}, "
            f"vocabulary={len(vectorizer.vocabulary_):,}"
        )

    if data["pairwise_score"].isna().any():
        raise ValueError("Some rows have no out-of-fold score.")

    output = data[
        ["row_id", "experiment_id", "fold",
         "relative_ctr", "pairwise_score"]
    ].copy()

    output.to_csv(OUTPUT_PATH, index=False)

    print("\nWEIGHTED PAIRWISE TRAINING COMPLETE")
    print(f"Rows scored: {len(output):,}")
    print(f"Experiments: {output['experiment_id'].nunique():,}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
