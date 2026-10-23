
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TARGETS_FILE = PROCESSED_DIR / "phase24_modeling_targets.csv"
EMBEDDINGS_FILE = PROCESSED_DIR / "phase24_headline_embeddings.npz"


def normalize_ids(values):
    return pd.Series(values).astype(str).reset_index(drop=True)


def main():
    print("PHASE 2.4 — EMBEDDING VALIDATION")
    print("-" * 45)

    if not TARGETS_FILE.exists():
        raise FileNotFoundError(f"Targets file not found: {TARGETS_FILE}")

    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(f"Embeddings file not found: {EMBEDDINGS_FILE}")

    targets = pd.read_csv(TARGETS_FILE)

    required_columns = {"row_id", "experiment_id", "headline"}
    missing_columns = required_columns - set(targets.columns)
    if missing_columns:
        raise ValueError(f"Missing target columns: {sorted(missing_columns)}")

    if targets["row_id"].isna().any() or targets["row_id"].duplicated().any():
        raise ValueError("Target row_id values must be present and unique.")

    # This artifact was generated locally by the project's embedding script.
    # allow_pickle=True is needed because experiment_id was saved as object dtype.
    with np.load(EMBEDDINGS_FILE, allow_pickle=True) as artifact:
        required_arrays = {"row_id", "experiment_id", "embeddings"}
        missing_arrays = required_arrays - set(artifact.files)
        if missing_arrays:
            raise ValueError(
                f"Missing arrays in embedding artifact: {sorted(missing_arrays)}"
            )

        saved_row_ids = artifact["row_id"].copy()
        saved_experiment_ids = artifact["experiment_id"].copy()
        embeddings = artifact["embeddings"].copy()

    if embeddings.ndim != 2:
        raise ValueError(f"Expected a 2D matrix, got {embeddings.shape}")

    if embeddings.shape != (len(targets), 384):
        raise ValueError(
            f"Expected ({len(targets)}, 384), got {embeddings.shape}"
        )

    if len(saved_row_ids) != len(targets):
        raise ValueError("Embedding row count does not match target row count.")

    if len(saved_experiment_ids) != len(targets):
        raise ValueError("Experiment ID count does not match target row count.")

    if not np.issubdtype(embeddings.dtype, np.number):
        raise ValueError(f"Embeddings are not numeric: {embeddings.dtype}")

    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings contain NaN or infinite values.")

    norms = np.linalg.norm(embeddings, axis=1)
    if np.any(norms == 0):
        raise ValueError("Found zero-length embedding vectors.")

    if not np.allclose(norms, 1.0, atol=1e-3):
        raise ValueError(
            f"Expected normalized embeddings; norm range is "
            f"{norms.min():.6f} to {norms.max():.6f}"
        )

    target_ids = normalize_ids(targets["row_id"])
    embedding_ids = normalize_ids(saved_row_ids)

    if embedding_ids.duplicated().any():
        raise ValueError("Embedding row IDs are not unique.")

    if set(target_ids) != set(embedding_ids):
        raise ValueError("Target and embedding row IDs do not match.")

    target_metadata = pd.DataFrame({
        "row_id": target_ids,
        "experiment_id_target": normalize_ids(targets["experiment_id"]),
    })

    embedding_metadata = pd.DataFrame({
        "row_id": embedding_ids,
        "experiment_id_embedding": normalize_ids(saved_experiment_ids),
    })

    aligned = embedding_metadata.merge(
        target_metadata,
        on="row_id",
        how="left",
        validate="one_to_one",
    )

    if not aligned["experiment_id_embedding"].equals(
        aligned["experiment_id_target"]
    ):
        raise ValueError("Experiment IDs do not match their row IDs.")

    print(f"Target rows:             {len(targets):,}")
    print(f"Embedding rows:          {len(embeddings):,}")
    print(f"Unique experiments:      {targets['experiment_id'].nunique():,}")
    print(f"Embedding dimensions:    {embeddings.shape[1]}")
    print(f"Data type:               {embeddings.dtype}")
    print(f"All values finite:       {np.isfinite(embeddings).all()}")
    print(f"Normalized vectors:      {np.allclose(norms, 1.0, atol=1e-3)}")
    print("Row IDs aligned:         True")
    print("Experiment IDs aligned:  True")
    print("\nEMBEDDING VALIDATION PASSED")


if __name__ == "__main__":
    main()
