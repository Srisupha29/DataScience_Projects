
# To rebuild cleaned stock data, macro data, audit outputs, and aligned macro features.

from pathlib import Path
import pandas as pd


# Project Path

PROJECT_ROOT = Path(__file__).resolve().parent

STOCK_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "stocks"
MACRO_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "market_macro"

PROCESSED_DIR = (
    PROJECT_ROOT / "notebooks" / "data" / "processed"
)
CLEAN_STOCK_DIR = PROCESSED_DIR / "stocks"
CLEAN_MACRO_DIR = PROCESSED_DIR / "market_macro"

for directory in [PROCESSED_DIR, CLEAN_STOCK_DIR, CLEAN_MACRO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

if not STOCK_RAW_DIR.exists():
    raise FileNotFoundError(f"Raw stock directory not found: {STOCK_RAW_DIR}")

if not MACRO_RAW_DIR.exists():
    raise FileNotFoundError(f"Raw macro directory not found: {MACRO_RAW_DIR}")


# Cleaning Function 

CLOSE_ONLY_FILES = {"INR_X", "BZ_F"}
cleaning_log = []


def standardize_index(data):
    """Convert index to timezone-naive normalized dates."""
    data = data.copy()
    dates = pd.DatetimeIndex(pd.to_datetime(data.index))

    if dates.tz is not None:
        dates = dates.tz_localize(None)

    data.index = dates.normalize()
    return data


def clean_dataset(file_path, output_dir, dataset_type):
    data = pd.read_parquet(file_path).copy()

    # Flatten Yahoo Finance MultiIndex columns when present.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)

    data.columns = [str(col).strip() for col in data.columns]
    data = standardize_index(data)

    if "Close" not in data.columns:
        raise ValueError(f"'Close' column missing from {file_path.name}")

    original_rows = len(data)

    duplicate_dates = int(data.index.duplicated(keep="last").sum())
    data = data.loc[~data.index.duplicated(keep="last")].copy()

    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")

    missing_close = int(data["Close"].isna().sum())
    nonpositive_close = int((data["Close"] <= 0).sum())

    data = data.loc[
        data["Close"].notna() & (data["Close"] > 0)
    ].copy()

    excluded_columns = []

    if file_path.stem in CLOSE_ONLY_FILES:
        excluded_columns = [
            column for column in ["Open", "High", "Low"]
            if column in data.columns
        ]
        data = data.drop(columns=excluded_columns)

    output_path = output_dir / file_path.name
    data.to_parquet(output_path)

    cleaning_log.append({
        "dataset": file_path.stem,
        "type": dataset_type,
        "original_rows": original_rows,
        "duplicate_dates_removed": duplicate_dates,
        "missing_close_removed": missing_close,
        "nonpositive_close_removed": nonpositive_close,
        "excluded_columns": ", ".join(excluded_columns),
        "clean_rows": len(data),
        "first_date": data.index.min().date() if len(data) else None,
        "last_date": data.index.max().date() if len(data) else None,
        "output_file": str(output_path)
    })


# Rebuild cleaned stock and macro data

stock_files = sorted(STOCK_RAW_DIR.glob("*.parquet"))
macro_files = sorted(MACRO_RAW_DIR.glob("*.parquet"))

if not stock_files:
    raise FileNotFoundError(f"No raw stock Parquet files found in {STOCK_RAW_DIR}")

if not macro_files:
    raise FileNotFoundError(f"No raw macro Parquet files found in {MACRO_RAW_DIR}")

for file_path in stock_files:
    clean_dataset(file_path, CLEAN_STOCK_DIR, "stock")

for file_path in macro_files:
    clean_dataset(file_path, CLEAN_MACRO_DIR, "market_macro")

cleaning_log_df = pd.DataFrame(cleaning_log)
cleaning_log_df.to_csv(PROCESSED_DIR / "cleaning_log.csv", index=False)


# Load Nifty Reference trading calendar

nifty_path = CLEAN_MACRO_DIR / "NSEI.parquet"

if not nifty_path.exists():
    raise FileNotFoundError(
        f"NIFTY cleaned macro file is required: {nifty_path}"
    )

nifty = pd.read_parquet(nifty_path)

if isinstance(nifty.columns, pd.MultiIndex):
    nifty.columns = nifty.columns.get_level_values(-1)

nifty = standardize_index(nifty)

nifty = nifty.loc[
    nifty["Close"].notna() & (nifty["Close"] > 0)
].sort_index()

nifty = nifty.loc[~nifty.index.duplicated(keep="last")]
nifty_dates = pd.DatetimeIndex(nifty.index.unique()).sort_values()

# Missing Observation and large return audits

missing_results = []
jump_results = []

for file_path in stock_files:
    clean_path = CLEAN_STOCK_DIR / file_path.name
    data = pd.read_parquet(clean_path)
    data = standardize_index(data)

    close = data["Close"].dropna().astype(float).sort_index()

    if close.empty:
        continue

    expected_dates = nifty_dates[
        (nifty_dates >= close.index.min())
        & (nifty_dates <= close.index.max())
    ]

    missing_dates = expected_dates.difference(close.index)

    missing_results.append({
        "ticker": file_path.stem,
        "missing_sessions": len(missing_dates),
        "missing_date_examples": [
            str(date.date()) for date in missing_dates[:10]
        ]
    })

    aligned_close = close.reindex(expected_dates)
    previous_close = aligned_close.shift(1)

    daily_returns = aligned_close.div(previous_close).sub(1)

    consecutive_observations = (
        aligned_close.notna() & previous_close.notna()
    )
    daily_returns = daily_returns.loc[consecutive_observations]

    large_moves = daily_returns.loc[daily_returns.abs() > 0.15]

    for date, daily_return in large_moves.items():
        jump_results.append({
            "ticker": file_path.stem,
            "date": date.date(),
            "daily_return_pct": round(daily_return * 100, 2),
            "previous_close": previous_close.loc[date],
            "current_close": aligned_close.loc[date]
        })

missing_audit = pd.DataFrame(
    missing_results,
    columns=["ticker", "missing_sessions", "missing_date_examples"]
)
missing_audit.to_csv(
    PROCESSED_DIR / "missing_observation_audit.csv",
    index=False
)

large_return_audit = pd.DataFrame(
    jump_results,
    columns=[
        "ticker", "date", "daily_return_pct",
        "previous_close", "current_close"
    ]
)

if not large_return_audit.empty:
    large_return_audit = large_return_audit.sort_values(
        "daily_return_pct",
        key=lambda values: values.abs(),
        ascending=False
    )

large_return_audit.to_csv(
    PROCESSED_DIR / "large_price_movements.csv",
    index=False
)

 
# Align macroeconomic data to nifty calendar

macro_config = {
    "INDIA_VIX": {"file": "INDIAVIX.parquet", "lag": 0},
    "USD_INR": {"file": "INR_X.parquet", "lag": 1},
    "BRENT_CRUDE": {"file": "BZ_F.parquet", "lag": 1},
    "US_10Y_YIELD": {"file": "TNX.parquet", "lag": 1}
}

aligned_macro = pd.DataFrame(index=nifty_dates)
aligned_macro.index.name = "Date"
aligned_macro["NIFTY_50_Close"] = nifty["Close"].reindex(nifty_dates)

alignment_checks = []

for name, config in macro_config.items():
    source_path = CLEAN_MACRO_DIR / config["file"]

    if not source_path.exists():
        raise FileNotFoundError(f"Required macro file not found: {source_path}")

    data = pd.read_parquet(source_path)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)

    data = standardize_index(data)

    source = data[["Close"]].copy()
    source["Close"] = pd.to_numeric(source["Close"], errors="coerce")
    source = source.loc[
        source["Close"].notna() & (source["Close"] > 0)
    ].sort_index()

    source = source.loc[~source.index.duplicated(keep="last")]
    source_dates = pd.DatetimeIndex(source.index)

    cutoff_dates = pd.Series(nifty_dates, index=nifty_dates).shift(
        config["lag"]
    )
    cutoff_index = pd.DatetimeIndex(cutoff_dates)

    valid_cutoffs = ~cutoff_index.isna()
    positions = source_dates.searchsorted(
        cutoff_index[valid_cutoffs],
        side="right"
    ) - 1

    values = pd.Series(float("nan"), index=nifty_dates, dtype="float64")
    source_date_used = pd.Series(
        pd.NaT, index=nifty_dates, dtype="datetime64[ns]"
    )

    available = positions >= 0
    target_dates = nifty_dates[valid_cutoffs][available]
    source_positions = positions[available]

    values.loc[target_dates] = (
        source["Close"].iloc[source_positions].to_numpy()
    )
    source_date_used.loc[target_dates] = source_dates[source_positions]

    aligned_macro[f"{name}_Close"] = values
    aligned_macro[f"{name}_Source_Date"] = source_date_used

    invalid = (
        source_date_used.notna()
        & (source_date_used > cutoff_dates)
    )

    alignment_checks.append({
        "dataset": name,
        "lag_sessions": config["lag"],
        "available_values": int(source_date_used.notna().sum()),
        "missing_values": int(source_date_used.isna().sum()),
        "future_information_violations": int(invalid.sum())
    })

alignment_validation = pd.DataFrame(alignment_checks)

aligned_macro.to_parquet(
    PROCESSED_DIR / "market_macro_aligned.parquet"
)
alignment_validation.to_csv(
    PROCESSED_DIR / "macro_alignment_validation.csv",
    index=False
)

print("Data Rebuild Completed")

print(f"Stock datasets cleaned: {len(stock_files)}")
print(f"Macro datasets cleaned: {len(macro_files)}")
print(f"Total datasets cleaned: {len(cleaning_log_df)}")
print(f"Aligned macro dataset shape: {aligned_macro.shape}")
print(f"Missing-session audit rows: {len(missing_audit)}")
print(f"Large price movements flagged: {len(large_return_audit)}")

        
