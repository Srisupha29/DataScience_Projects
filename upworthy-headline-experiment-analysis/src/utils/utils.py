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

# Expected source dataset dimensions.
# These constants are validation expectations, not substitutes
# for measuring the actual dataset.
EXPECTED_PACKAGE_ROWS = 22666
EXPECTED_EXPERIMENTS = 4873

# Project-defined screening window; source documentation has not yet
# been verified to establish this as an official randomization-risk period.
RANDOMIZATION_RISK_START = "2013-06-25"
RANDOMIZATION_RISK_END = "2014-01-10"

# Project-defined diagnostic threshold, not a statistical significance
# cutoff. Ratios above this value are flagged for manual review.
IMPRESSION_IMBALANCE_THRESHOLD = 1.5

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


def normalize_headline_sql(column_name="headline"):
    """Return a SQL expression that normalizes headline case and whitespace."""
    return f"LOWER(TRIM({column_name}))"


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
