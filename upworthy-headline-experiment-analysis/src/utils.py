
from pathlib import Path

import duckdb


# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Source dataset
RAW_FILE = (
    RAW_DIR
    / "upworthy-archive-exploratory-packages-03.12.2020.csv"
)

# Processed datasets
PACKAGES_FILE = PROCESSED_DIR / "packages.parquet"
EDITORIAL_FILE = PROCESSED_DIR / "editorial_metadata.parquet"
EXPERIMENT_SUMMARY_FILE = (
    PROCESSED_DIR / "experiment_summary.parquet"
)
COMPARISON_CANDIDATES_FILE = (
    PROCESSED_DIR / "comparison_candidates.parquet"
)
IMPRESSION_BALANCE_FILE = (
    PROCESSED_DIR / "impression_balance.parquet"
)
WITHIN_EXPERIMENT_FILE = (
    PROCESSED_DIR / "within_experiment_comparisons.parquet"
)

# Explicit schema for the source CSV.
# DuckDB will use these types instead of inferring them.
RAW_COLUMN_TYPES = {
    "column00": "BIGINT",
    "created_at": "TIMESTAMP",
    "updated_at": "TIMESTAMP",
    "clickability_test_id": "VARCHAR",
    "excerpt": "VARCHAR",
    "headline": "VARCHAR",
    "lede": "VARCHAR",
    "slug": "VARCHAR",
    "eyecatcher_id": "VARCHAR",
    "impressions": "BIGINT",
    "clicks": "BIGINT",
    "significance": "DOUBLE",
    "first_place": "BOOLEAN",
    "winner": "BOOLEAN",
    "share_text": "VARCHAR",
    "square": "VARCHAR",
    "test_week": "BIGINT",
}


def get_connection():
    """Return an in-memory DuckDB connection."""
    return duckdb.connect(database=":memory:")


def load_raw_view(con, view_name="source_packages"):
    """Load the source CSV using its declared column types."""
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source CSV not found: {RAW_FILE}"
        )

    con.read_csv(
        str(RAW_FILE),
        header=True,
        columns=RAW_COLUMN_TYPES,
    ).create_view(view_name)


def load_parquet_view(con, view_name, parquet_file):
    """Load a processed Parquet file as a DuckDB view."""
    if not parquet_file.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {parquet_file}"
        )

    con.read_parquet(
        str(parquet_file)
    ).create_view(view_name)
