from pathlib import Path

import hashlib
import subprocess
import sys

import pandas as pd
import pytest

# Project Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_STOCK_DIR = PROJECT_ROOT / "data" / "raw" / "stocks"
RAW_MACRO_DIR = PROJECT_ROOT / "data" / "raw" / "market_macro"

PROCESSED_ROOT = PROJECT_ROOT / "notebooks" / "data" / "processed"
CLEAN_STOCK_DIR = PROCESSED_ROOT / "stocks"
CLEAN_MACRO_DIR = PROCESSED_ROOT / "market_macro"

CLEANING_LOG = PROCESSED_ROOT / "cleaning_log.csv"


def find_aligned_file():
    matches = list(PROCESSED_ROOT.rglob("market_macro_aligned.parquet"))
    return matches[0] if len(matches) == 1 else None

EXPECTED_STOCK_COUNT = 50
EXPECTED_MACRO_COUNT = 5

# These macro series are aligned to the same NIFTY session
SAME_SESSION_MACRO = ["INDIA_VIX"]

# These series are conservatively lagged by at least one NIFTY session
LAGGED_MACRO = ["USD_INR", "BRENT_CRUDE", "US_10Y_YIELD"]


# Helpers

def parquet_files(directory):
    # Return Parquet files directly inside a directory
    if not directory.exists():
        return []
    return sorted(directory.glob("*.parquet"))


def read_parquet(path):
    # Read a Parquet file and return a DataFrame
    return pd.read_parquet(path)


def get_date_values(data):
    # Support datasets where the date is either a column or the DataFrame index
    
    date_column = next(
        (
            column
            for column in data.columns
            if str(column).strip().lower() in {"date", "datetime", "timestamp"}
        ),
        None,
    )

    if date_column is not None:
        dates = pd.to_datetime(data[date_column], errors="coerce")
    else:
        dates = pd.to_datetime(data.index, errors="coerce")

    return pd.DatetimeIndex(dates)


def get_column(data, name):
    # Find a column case-insensitively 
    matches = [
        column
        for column in data.columns
        if str(column).strip().lower() == name.lower()
    ]

    if not matches:
        return None

    return matches[0]


def sha256(path):
    # Calculate a file checksum without loading the whole file into memory 
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def all_raw_files():
    return (
        parquet_files(RAW_STOCK_DIR)
        + parquet_files(RAW_MACRO_DIR)
    )

# File and Data Completeness

def test_required_directories_and_files_exist():
    required_paths = [
        RAW_STOCK_DIR,
        RAW_MACRO_DIR,
        CLEAN_STOCK_DIR,
        CLEAN_MACRO_DIR,
        CLEANING_LOG,
    ]

    missing = [str(path) for path in required_paths if not path.exists()]

    assert not missing, f"Missing required paths: {missing}"

    aligned_matches = list(PROCESSED_ROOT.rglob("market_macro_aligned.parquet"))
    assert len(aligned_matches) == 1, (
        "Expected exactly one market_macro_aligned.parquet under "
        f"{PROCESSED_ROOT}; found {len(aligned_matches)}."
    )


def test_raw_dataset_counts():
    assert len(parquet_files(RAW_STOCK_DIR)) == EXPECTED_STOCK_COUNT
    assert len(parquet_files(RAW_MACRO_DIR)) == EXPECTED_MACRO_COUNT


def test_cleaned_dataset_counts():
    stock_files = parquet_files(CLEAN_STOCK_DIR)
    macro_files = [
        path for path in parquet_files(CLEAN_MACRO_DIR)
        if "aligned" not in path.stem.lower()
    ]

    assert len(stock_files) == EXPECTED_STOCK_COUNT, (
        f"Expected {EXPECTED_STOCK_COUNT} cleaned stock files; "
        f"found {len(stock_files)}."
    )

    assert len(macro_files) == EXPECTED_MACRO_COUNT, (
        f"Expected {EXPECTED_MACRO_COUNT} cleaned macro files; "
        f"found {len(macro_files)}."
    )
    
# Date, Price and OHLC

def validate_clean_dataset(path, check_ohlc=True):
    data = read_parquet(path)

    assert not data.empty, f"{path.name} is empty."

    dates = get_date_values(data)

    assert dates.notna().all(), f"{path.name} contains invalid dates."
    assert dates.is_unique, f"{path.name} contains duplicate dates."
    assert dates.is_monotonic_increasing, (
        f"{path.name} dates are not sorted in ascending order."
    )

    close_column = get_column(data, "Close")
    assert close_column is not None, f"{path.name} has no Close column."

    close = pd.to_numeric(data[close_column], errors="coerce")

    assert close.notna().all(), f"{path.name} contains missing/non-numeric Close."
    assert (close > 0).all(), f"{path.name} contains nonpositive Close prices."

    if check_ohlc:
        open_column = get_column(data, "Open")
        high_column = get_column(data, "High")
        low_column = get_column(data, "Low")

        # Some macro series intentionally retain Close only.
        if all(column is not None for column in [
            open_column, high_column, low_column
        ]):
            open_price = pd.to_numeric(data[open_column], errors="coerce")
            high_price = pd.to_numeric(data[high_column], errors="coerce")
            low_price = pd.to_numeric(data[low_column], errors="coerce")

            assert high_price.notna().all(), (
                f"{path.name} contains missing/non-numeric High values."
            )
            assert low_price.notna().all(), (
                f"{path.name} contains missing/non-numeric Low values."
            )
            assert open_price.notna().all(), (
                f"{path.name} contains missing/non-numeric Open values."
            )

            assert (high_price >= low_price).all(), (
                f"{path.name} contains High < Low."
            )
            assert (high_price >= open_price).all(), (
                f"{path.name} contains High < Open."
            )
            assert (high_price >= close).all(), (
                f"{path.name} contains High < Close."
            )
            assert (low_price <= open_price).all(), (
                f"{path.name} contains Low > Open."
            )
            assert (low_price <= close).all(), (
                f"{path.name} contains Low > Close."
            )


@pytest.mark.parametrize(
    "path",
    parquet_files(CLEAN_STOCK_DIR),
    ids=lambda path: path.stem,
)
def test_stock_dataset_integrity(path):
    validate_clean_dataset(path, check_ohlc=True)


@pytest.mark.parametrize(
    "path",
    [
        path for path in parquet_files(CLEAN_MACRO_DIR)
        if "aligned" not in path.stem.lower()
    ],
    ids=lambda path: path.stem,
)
def test_macro_dataset_integrity(path):
    # USD/INR and Brent intentionally retain Close only.
    validate_clean_dataset(path, check_ohlc=True)

# 5. Macro Alignment and Checks

def test_macro_alignment_file_structure():
    aligned_path = find_aligned_file()
    assert aligned_path is not None, (
        "Could not uniquely locate market_macro_aligned.parquet."
    )
    aligned = read_parquet(aligned_path)

    assert not aligned.empty, "Aligned macro dataset is empty."

    required_columns = [
        "NIFTY_50_Close",
        "INDIA_VIX_Close",
        "USD_INR_Close",
        "BRENT_CRUDE_Close",
        "US_10Y_YIELD_Close",
        "INDIA_VIX_Source_Date",
        "USD_INR_Source_Date",
        "BRENT_CRUDE_Source_Date",
        "US_10Y_YIELD_Source_Date",
    ]

    missing = [column for column in required_columns if column not in aligned.columns]

    assert not missing, f"Aligned dataset is missing columns: {missing}"

    assert len(aligned) == 4138, (
        f"Expected 4,138 NIFTY sessions; found {len(aligned)}."
    )

    dates = get_date_values(aligned)

    assert dates.notna().all(), "Aligned dataset contains invalid dates."
    assert dates.is_unique, "Aligned dataset contains duplicate dates."
    assert dates.is_monotonic_increasing, (
        "Aligned dataset dates are not sorted."
    )


def test_macro_alignment_has_no_future_source_dates():
    aligned_path = find_aligned_file()
    assert aligned_path is not None, (
        "Could not uniquely locate market_macro_aligned.parquet."
    )
    aligned = read_parquet(aligned_path)
    target_dates = get_date_values(aligned)

    for series in SAME_SESSION_MACRO + LAGGED_MACRO:
        source_date_column = f"{series}_Source_Date"

        assert source_date_column in aligned.columns, (
            f"Missing audit column: {source_date_column}"
        )

        source_dates = pd.to_datetime(
            aligned[source_date_column],
            errors="coerce",
        )

        available = source_dates.notna()

        assert (
            source_dates[available].to_numpy()
            <= target_dates[available].to_numpy()
        ).all(), f"{series} contains a future source date."

        if series in LAGGED_MACRO:
            assert (
                source_dates[available].to_numpy()
                < target_dates[available].to_numpy()
            ).all(), (
                f"{series} should use a prior NIFTY session, "
                "but a same-day source date was found."
            )

# Audit file integrity

def test_cleaning_log_covers_all_datasets():
    log = pd.read_csv(CLEANING_LOG)

    required_columns = {
        "dataset",
        "original_rows",
        "clean_rows",
        "first_date",
        "last_date",
        "output_file",
    }

    missing = required_columns.difference(log.columns)

    assert not missing, f"Cleaning log is missing columns: {sorted(missing)}"

    assert len(log) == EXPECTED_STOCK_COUNT + EXPECTED_MACRO_COUNT, (
        f"Expected 55 cleaning-log rows; found {len(log)}."
    )

    assert log["dataset"].notna().all()
    assert log["dataset"].is_unique
    assert (log["original_rows"] >= log["clean_rows"]).all()
    assert (log["clean_rows"] > 0).all()


def test_expected_audit_reports_exist():
    csv_files = list(PROCESSED_ROOT.rglob("*.csv"))

    # The pipeline should produce a cleaning log plus diagnostic reports.
    assert len(csv_files) >= 4, (
        "Expected cleaning log and diagnostic CSV reports; "
        f"found {len(csv_files)} CSV files."
    )

    names = {path.name.lower() for path in csv_files}

    assert any("missing" in name for name in names), (
        "Missing-observation audit CSV was not found."
    )
    assert any(
        "movement" in name or "anomal" in name or "large" in name
        for name in names
    ), "Large-price-movement audit CSV was not found."


# Raw Data Preservation during test execution
def test_rebuild_does_not_modify_raw_data():
    raw_files = all_raw_files()

    assert len(raw_files) == EXPECTED_STOCK_COUNT + EXPECTED_MACRO_COUNT, (
        f"Expected 55 raw Parquet files; found {len(raw_files)}."
    )

    before = {path: sha256(path) for path in raw_files}

    rebuild_script = PROJECT_ROOT / "rebuild_data.py"
    assert rebuild_script.exists(), "rebuild_data.py was not found in project root."

    # Run the actual rebuild using the same Python interpreter as pytest.
    result = subprocess.run(
        [sys.executable, str(rebuild_script)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=1800,
    )

    assert result.returncode == 0, (
        "The rebuild command failed during the preservation test.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    after = {path: sha256(path) for path in raw_files}

    changed = [
        str(path)
        for path in before
        if before[path] != after.get(path)
    ]

    assert not changed, f"Rebuild modified raw files: {changed}"


# Note to Self: python -m pytest -v tests/test_data_quality.py