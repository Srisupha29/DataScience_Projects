
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRanker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TARGETS_FILE = PROCESSED_DIR / "phase24_modeling_targets.csv"
FEATURES_FILE = PROCESSED_DIR / "phase24_modeling_features.csv"
FOLDS_FILE = PROCESSED_DIR / "phase24_cv_folds.csv"
EMBEDDINGS_FILE = PROCESSED_DIR / "phase24_headline_embeddings_mpnet.npz"
OUTPUT_FILE = PROCESSED_DIR / "phase24_embedding_ensemble_mpnet_oof_predictions.csv"
BASELINE_FILE = PROCESSED_DIR / "phase24_pairwise_oof_predictions.csv"

RANDOM_STATE = 42
N_PCA_COMPONENTS = 32
MIN_CTR_DIFFERENCE = 0.0005


def percentile_rank(values):
    """Return within-experiment percentile ranks."""
    return values.rank(method="average", pct=True)


def build_pairwise_training_data(X, frame):
    """Create both orientations of each non-near-tied headline pair."""
    pair_left = []
    pair_right = []
    pair_weights = []

    for _, positions in frame.groupby("experiment_id", sort=False).indices.items():
        positions = np.asarray(positions, dtype=int)

        if len(positions) < 2:
            continue

        ctr = frame.iloc[positions]["relative_ctr"].to_numpy()

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                difference = ctr[i] - ctr[j]

                if abs(difference) < MIN_CTR_DIFFERENCE:
                    continue

                left = positions[i]
                right = positions[j]
                weight = abs(difference)

                # Correctly orient the pair so the higher-CTR variant wins.
                if difference < 0:
                    left, right = right, left

                pair_left.extend([left, right])
                pair_right.extend([right, left])
                pair_weights.extend([weight, weight])

    if not pair_left:
        raise ValueError("No comparable training pairs remain after tie filtering.")

    pair_weights = np.asarray(pair_weights, dtype=float)
    pair_weights /= pair_weights.mean()

    differences = X[pair_left] - X[pair_right]
    labels = np.tile([1, 0], len(pair_left) // 2)

    return differences, labels, pair_weights


def main():
    for path in [
        TARGETS_FILE,
        FEATURES_FILE,
        FOLDS_FILE,
        EMBEDDINGS_FILE,
        BASELINE_FILE,
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    targets = pd.read_csv(TARGETS_FILE)
    features = pd.read_csv(FEATURES_FILE)
    folds = pd.read_csv(FOLDS_FILE)
    baseline = pd.read_csv(BASELINE_FILE)

    with np.load(EMBEDDINGS_FILE, allow_pickle=True) as artifact:
        embedding_row_ids = artifact["row_id"].astype(str)
        embedding_experiment_ids = artifact["experiment_id"].astype(str)
        embeddings = artifact["embeddings"].astype(np.float32)

    # Normalize join keys.
    for frame in [targets, features, folds, baseline]:
        if "row_id" not in frame.columns:
            raise ValueError("A required input file has no row_id column.")
        frame["row_id"] = frame["row_id"].astype(str)

    if "fold" not in folds.columns:
        raise ValueError("The folds file must contain a 'fold' column.")

    if "relative_ctr" not in targets.columns:
        raise ValueError("Targets file must contain 'relative_ctr'.")

    if "headline" not in targets.columns:
        raise ValueError("Targets file must contain 'headline'.")

    if "pairwise_score" not in baseline.columns:
        raise ValueError("Baseline file must contain 'pairwise_score'.")

    # The target file is the authoritative row and experiment mapping.
    data = targets[
        ["row_id", "experiment_id", "headline", "relative_ctr"]
    ].copy()
    data["experiment_id"] = data["experiment_id"].astype(str)

    if data["row_id"].duplicated().any():
        raise ValueError("Duplicate row_id values in targets.")

    # Join folds and engineered headline features.
    data = data.merge(
        folds[["row_id", "fold"]],
        on="row_id",
        how="left",
        validate="one_to_one",
    )

    if data["fold"].isna().any():
        raise ValueError("Some target rows are missing fold assignments.")

    if features["row_id"].duplicated().any():
        raise ValueError("Duplicate row_id values in feature file.")

    feature_columns = [
        column
        for column in features.select_dtypes(include=[np.number]).columns
        if column != "row_id"
        and not any(
            term in column.lower()
            for term in [
                "click", "impression", "ctr", "target", "winner",
                "conversion", "relative", "fold",
            ]
        )
    ]

    if not feature_columns:
        raise ValueError(
            "No numeric headline features found in phase24_modeling_features.csv."
        )

    numeric_features = features[["row_id"] + feature_columns].copy()

    data = data.merge(
        numeric_features,
        on="row_id",
        how="left",
        validate="one_to_one",
    )

    if data[feature_columns].isna().any().any():
        raise ValueError("Numeric headline features contain missing values.")

    # Verify exact embedding-to-target alignment.
    embedding_metadata = pd.DataFrame({
        "row_id": embedding_row_ids,
        "embedding_experiment_id": embedding_experiment_ids,
    })

    if embedding_metadata["row_id"].duplicated().any():
        raise ValueError("Duplicate row IDs in embedding artifact.")

    data = data.merge(
        embedding_metadata,
        on="row_id",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    if not data["_merge"].eq("both").all():
        raise ValueError("Embedding rows do not cover every target row.")

    if not (
        data["experiment_id"].to_numpy()
        == data["embedding_experiment_id"].to_numpy()
    ).all():
        raise ValueError("Embedding experiment IDs do not match targets.")

    data = data.drop(columns=["_merge", "embedding_experiment_id"])

    # Align embedding matrix to target row order.
    embedding_lookup = {
        row_id: position
        for position, row_id in enumerate(embedding_row_ids)
    }
    embedding_positions = data["row_id"].map(embedding_lookup).to_numpy()
    embeddings = embeddings[embedding_positions]

    # Center embeddings within each experiment.
    # This uses only headline representations, never target values.
    centered_embeddings = embeddings.copy()
    experiment_ids = data["experiment_id"].to_numpy()

    for experiment_id in pd.unique(experiment_ids):
        mask = experiment_ids == experiment_id
        centered_embeddings[mask] -= centered_embeddings[mask].mean(axis=0)

    # Load baseline scores and align them to the target order.
    baseline = baseline[["row_id", "pairwise_score"]].copy()

    if baseline["row_id"].duplicated().any():
        raise ValueError("Baseline predictions contain duplicate row IDs.")

    data = data.merge(
        baseline,
        on="row_id",
        how="left",
        validate="one_to_one",
    )

    if data["pairwise_score"].isna().any():
        raise ValueError("Some rows are missing baseline pairwise predictions.")

    headlines = data["headline"].fillna("").astype(str)
    numeric_values = data[feature_columns].to_numpy(dtype=float)

    oof_pairwise = np.full(len(data), np.nan)
    oof_ranker = np.full(len(data), np.nan)

    fold_values = sorted(data["fold"].unique())

    print("PHASE 2.4 — EMBEDDING AND ENSEMBLE TRAINING")
    print(f"Rows: {len(data):,}")
    print(f"Experiments: {data['experiment_id'].nunique():,}")
    print(f"Numeric headline features: {len(feature_columns)}")
    print(f"Folds: {len(fold_values)}")

    for fold in fold_values:
        train_mask = data["fold"].to_numpy() != fold
        valid_mask = data["fold"].to_numpy() == fold

        train_rows = data.loc[train_mask].copy().reset_index(drop=True)
        valid_rows = data.loc[valid_mask].copy().reset_index(drop=True)

        train_headlines = headlines.loc[train_mask].tolist()
        valid_headlines = headlines.loc[valid_mask].tolist()

        print(f"\nFold {fold}: train={len(train_rows):,}, validation={len(valid_rows):,}")

        # Fit TF-IDF only on this fold's training headlines.
        tfidf = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=5,
            max_features=1000,
            sublinear_tf=True,
        )

        X_train_tfidf = tfidf.fit_transform(train_headlines)
        X_valid_tfidf = tfidf.transform(valid_headlines)

        # Fit numeric scaling only on training data.
        scaler = StandardScaler()
        X_train_numeric = scaler.fit_transform(numeric_values[train_mask])
        X_valid_numeric = scaler.transform(numeric_values[valid_mask])

        # Fit PCA only on training embeddings.
        n_components = min(
            N_PCA_COMPONENTS,
            centered_embeddings[train_mask].shape[0] - 1,
            centered_embeddings.shape[1],
        )

        pca = PCA(n_components=n_components, random_state=RANDOM_STATE)
        train_pca = pca.fit_transform(centered_embeddings[train_mask])
        valid_pca = pca.transform(centered_embeddings[valid_mask])

        pca_scaler = StandardScaler()
        train_pca = pca_scaler.fit_transform(train_pca)
        valid_pca = pca_scaler.transform(valid_pca)

        X_train = hstack(
            [X_train_tfidf, X_train_numeric, train_pca],
            format="csr",
        )
        X_valid = hstack(
            [X_valid_tfidf, X_valid_numeric, valid_pca],
            format="csr",
        )

        # Weighted pairwise logistic model.
        pair_X, pair_y, pair_weights = build_pairwise_training_data(
            X_train, train_rows
        )

        pairwise_model = LogisticRegression(
            C=0.1,
            fit_intercept=False,
            max_iter=2000,
            random_state=RANDOM_STATE,
        )
        pairwise_model.fit(pair_X, pair_y, sample_weight=pair_weights)

        pairwise_scores = np.asarray(
            X_valid @ pairwise_model.coef_.ravel()
        ).ravel()

        valid_indices = np.flatnonzero(valid_mask)
        oof_pairwise[valid_indices] = pairwise_scores

        # XGBoost ranker: groups must be contiguous and group sizes supplied.
        train_sorted = train_rows.sort_values(
            ["experiment_id", "row_id"]
        ).reset_index(drop=True)

        train_order = train_rows.set_index("row_id").loc[
            train_sorted["row_id"]
        ].index
        original_train_positions = train_rows.reset_index().set_index(
            "row_id"
        ).loc[train_sorted["row_id"], "index"].to_numpy()

        X_rank_train = X_train[original_train_positions]
        rank_labels = (
            train_sorted.groupby("experiment_id")["relative_ctr"]
            .rank(method="dense")
            .astype(int)
            .to_numpy()
            - 1
        )

        group_sizes = (
            train_sorted.groupby("experiment_id", sort=False)
            .size()
            .to_list()
        )

        ranker = XGBRanker(
            objective="rank:pairwise",
            n_estimators=300,
            max_depth=3,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=5.0,
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=4,
        )

        ranker.fit(
            X_rank_train,
            rank_labels,
            group=group_sizes,
            verbose=False,
        )

        oof_ranker[valid_indices] = ranker.predict(X_valid)

        print("  Pairwise model and ranker trained.")

    if np.isnan(oof_pairwise).any() or np.isnan(oof_ranker).any():
        raise ValueError("OOF predictions are incomplete.")

    output = data[
        ["row_id", "experiment_id", "fold", "relative_ctr", "pairwise_score"]
    ].copy()

    output["embedding_pairwise_score"] = oof_pairwise
    output["xgb_rank_score"] = oof_ranker

    # Combine models using within-experiment percentile ranks.
    output["baseline_rank"] = output.groupby(
        "experiment_id"
    )["pairwise_score"].transform(percentile_rank)

    output["embedding_pairwise_rank"] = output.groupby(
        "experiment_id"
    )["embedding_pairwise_score"].transform(percentile_rank)

    output["xgb_rank"] = output.groupby(
        "experiment_id"
    )["xgb_rank_score"].transform(percentile_rank)

    output["ensemble_score"] = output[
        ["baseline_rank", "embedding_pairwise_rank", "xgb_rank"]
    ].mean(axis=1)

    output.to_csv(OUTPUT_FILE, index=False)

    print("\nTRAINING COMPLETE")
    print(f"Output rows: {len(output):,}")
    print(f"Saved: {OUTPUT_FILE}")
    print("Evaluation has not been finalized.")


if __name__ == "__main__":
    main()
