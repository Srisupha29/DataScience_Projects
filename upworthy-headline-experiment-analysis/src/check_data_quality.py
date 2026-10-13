
from pathlib import Path

import duckdb

# Locate the project and exploratory dataset.
PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"

csv_files = list(RAW_DIR.glob("*exploratory*.csv"))

if len(csv_files) != 1:
    raise RuntimeError(
        f"Expected exactly one exploratory CSV, found {len(csv_files)}"
    )

csv_path = str(csv_files[0]).replace("'", "''")

con = duckdb.connect()

con.execute(
    f"""
    CREATE VIEW upworthy AS
    SELECT *
    FROM read_csv_auto('{csv_path}')
    """
)

# 1. Check whether the source's row identifier is unique.
print("\n=== 1. ROW IDENTIFIER CHECK ===")

print(
    con.execute(
        """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT column00) AS distinct_row_ids,
            COUNT(*) - COUNT(DISTINCT column00) AS repeated_row_id_count
        FROM upworthy
        """
    ).df().to_string(index=False)
)

# 2. Find repeated experiment/headline combinations.
print("\n=== 2. REPEATED EXPERIMENT + HEADLINE COMBINATIONS ===")

print(
    con.execute(
        """
        SELECT
            clickability_test_id,
            headline,
            COUNT(*) AS row_count
        FROM upworthy
        GROUP BY clickability_test_id, headline
        HAVING COUNT(*) > 1
        ORDER BY row_count DESC
        LIMIT 20
        """
    ).df().to_string(index=False)
)

# 3. Check how many distinct headline texts each experiment has.
print("\n=== 3. EXPERIMENTS WITH FEWER DISTINCT HEADLINES THAN ROWS ===")

print(
    con.execute(
        """
        WITH experiment_structure AS (
            SELECT
                clickability_test_id,
                COUNT(*) AS row_count,
                COUNT(DISTINCT headline) AS distinct_headlines,
                COUNT(DISTINCT slug) AS distinct_slugs
            FROM upworthy
            GROUP BY clickability_test_id
        )
        SELECT *
        FROM experiment_structure
        WHERE distinct_headlines < row_count
        ORDER BY row_count DESC
        LIMIT 20
        """
    ).df().to_string(index=False)
)

# 4. Validate clicks and impressions.
print("\n=== 4. PERFORMANCE COUNT VALIDATION ===")

print(
    con.execute(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE impressions = 0
            ) AS zero_impression_rows,

            COUNT(*) FILTER (
                WHERE impressions IS NULL
            ) AS null_impression_rows,

            COUNT(*) FILTER (
                WHERE clicks IS NULL
            ) AS null_click_rows,

            COUNT(*) FILTER (
                WHERE clicks > impressions
            ) AS clicks_exceed_impressions,

            COUNT(*) FILTER (
                WHERE impressions < 0
            ) AS negative_impression_rows,

            COUNT(*) FILTER (
                WHERE clicks < 0
            ) AS negative_click_rows
        FROM upworthy
        """
    ).df().to_string(index=False)
)

# 5. Profile outcome-related fields; do not use them as predictors.
print("\n=== 5. WINNER / FIRST-PLACE / SIGNIFICANCE PROFILE ===")

print(
    con.execute(
        """
        SELECT
            COUNT(*) AS total_rows,

            COUNT(*) FILTER (
                WHERE winner IS TRUE
            ) AS winner_true_rows,

            COUNT(*) FILTER (
                WHERE winner IS FALSE
            ) AS winner_false_rows,

            COUNT(*) FILTER (
                WHERE winner IS NULL
            ) AS winner_null_rows,

            COUNT(*) FILTER (
                WHERE first_place IS TRUE
            ) AS first_place_true_rows,

            COUNT(*) FILTER (
                WHERE first_place IS FALSE
            ) AS first_place_false_rows,

            COUNT(*) FILTER (
                WHERE first_place IS NULL
            ) AS first_place_null_rows,

            COUNT(*) FILTER (
                WHERE significance IS NULL
            ) AS significance_null_rows,

            MIN(significance) AS min_significance,

            MEDIAN(significance) AS median_significance,

            MAX(significance) AS max_significance
        FROM upworthy
        """
    ).df().to_string(index=False)
)

print("\nQuality checks complete. No source data was modified.")

con.close()
