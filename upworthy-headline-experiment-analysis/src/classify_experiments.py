
from pathlib import Path
import duckdb

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

con.execute(
    """
    CREATE TEMP VIEW experiment_structure AS
    SELECT
        clickability_test_id,
        COUNT(*) AS package_count,
        COUNT(DISTINCT headline) AS distinct_headlines,
        COUNT(DISTINCT eyecatcher_id) AS distinct_images,
        COUNT(*) FILTER (
            WHERE eyecatcher_id IS NULL
        ) AS missing_image_id_rows
    FROM upworthy
    GROUP BY clickability_test_id
    """
)

print("HEADLINE × IMAGE VARIATION")
print("=" * 65)

cross_tab = con.execute(
    """
    SELECT
        CASE
            WHEN distinct_headlines = 1 THEN 'One headline'
            ELSE 'Multiple headlines'
        END AS headline_pattern,
        CASE
            WHEN missing_image_id_rows = package_count
                THEN 'All image IDs missing'
            WHEN distinct_images = 1
                THEN 'One distinct image ID'
            WHEN distinct_images > 1
                THEN 'Multiple distinct image IDs'
            ELSE 'Some image IDs missing; none identified'
        END AS image_pattern,
        COUNT(*) AS experiment_count
    FROM experiment_structure
    GROUP BY headline_pattern, image_pattern
    ORDER BY headline_pattern, image_pattern
    """
).df()

print(cross_tab.to_string(index=False))

print("\nIMAGE ID COMPLETENESS")
print("=" * 65)

image_quality = con.execute(
    """
    SELECT
        COUNT(*) AS total_experiments,
        SUM(CASE
            WHEN missing_image_id_rows = 0 THEN 1 ELSE 0
        END) AS experiments_with_no_missing_image_ids,
        SUM(CASE
            WHEN missing_image_id_rows > 0
             AND missing_image_id_rows < package_count
                THEN 1 ELSE 0
        END) AS experiments_with_some_missing_image_ids,
        SUM(CASE
            WHEN missing_image_id_rows = package_count
                THEN 1 ELSE 0
        END) AS experiments_with_all_image_ids_missing,
        SUM(missing_image_id_rows) AS total_rows_missing_image_id
    FROM experiment_structure
    """
).df()

print(image_quality.to_string(index=False))

print("\nAnalysis complete. Source CSV was not modified.")

con.close()
