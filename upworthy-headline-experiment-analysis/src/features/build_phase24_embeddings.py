
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TARGETS_FILE = PROCESSED_DIR / "phase24_modeling_targets.csv"
OUTPUT_FILE = PROCESSED_DIR / "phase24_headline_embeddings_mpnet.npz"

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
BATCH_SIZE = 32
EXPECTED_DIMENSIONS = 768


def main():
    targets = pd.read_csv(TARGETS_FILE)

    required = {"row_id", "experiment_id", "headline"}
    missing = required - set(targets.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if targets["row_id"].duplicated().any():
        raise ValueError("Duplicate row_id values detected.")

    headlines = targets["headline"].fillna("").astype(str).tolist()

    print(f"Rows: {len(targets):,}")
    print(f"Experiments: {targets['experiment_id'].nunique():,}")
    print(f"Loading embedding model: {MODEL_NAME}")
    print(f"Batch size: {BATCH_SIZE}")

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        headlines,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)

    expected_shape = (len(targets), EXPECTED_DIMENSIONS)

    if embeddings.shape != expected_shape:
        raise ValueError(
            f"Unexpected embedding shape: {embeddings.shape}; "
            f"expected {expected_shape}"
        )

    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings contain non-finite values.")

    norms = np.linalg.norm(embeddings, axis=1)

    if not np.allclose(norms, 1.0, atol=1e-4):
        raise ValueError("Embedding vectors are not unit-normalized.")

    np.savez_compressed(
        OUTPUT_FILE,
        row_id=targets["row_id"].to_numpy(),
        experiment_id=targets["experiment_id"].to_numpy(),
        embeddings=embeddings,
    )

    print("\nMPNET EMBEDDING GENERATION COMPLETE")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Data type: {embeddings.dtype}")
    print(f"All values finite: {np.isfinite(embeddings).all()}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
