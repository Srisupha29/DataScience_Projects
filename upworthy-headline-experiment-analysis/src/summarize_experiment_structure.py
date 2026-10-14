
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

# Summarize the structure of each experiment.
con.execute(
    """
    CREATE TEMP VIEW experiment_structure AS
    SELECT
        clickability_test_id,
        COUNT(*) AS package_count,
        COUNT(DISTINCT headline) AS distinct_headlines,
        COUNT(DISTINCT eyecatcher_id) AS distinct_images
    FROM upworthy
    GROUP BY clickability_test_id
    """
)

print("EXPERIMENT STRUCTURE SUMMARY")
print("=" * 60)

summary = con.execute(
    """
    SELECT
        COUNT(*) AS total_experiments,
        SUM(package_count) AS total_packages,
        SUM(CASE
            WHEN distinct_headlines > 1 THEN 1 ELSE 0
        END) AS experiments_with_multiple_headlines,
        SUM(CASE
            WHEN distinct_images > 1 THEN 1 ELSE 0
        END) AS experiments_with_multiple_images,
        SUM(CASE
            WHEN distinct_headlines = 1
             AND distinct_images = 1 THEN 1 ELSE 0
        END) AS experiments_with_one_headline_and_one_image
    FROM experiment_structure
    """
).df()

print(summary.to_string(index=False))

print("\nDISTRIBUTION OF HEADLINE VARIANTS")
print("=" * 60)

headline_distribution = con.execute(
    """
    SELECT
        distinct_headlines,
        COUNT(*) AS experiment_count
    FROM experiment_structure
    GROUP BY distinct_headlines
    ORDER BY distinct_headlines
    """
).df()

print(headline_distribution.to_string(index=False))

print("\nDISTRIBUTION OF IMAGE VARIANTS")
print("=" * 60)

image_distribution = con.execute(
    """
    SELECT
        distinct_images,
        COUNT(*) AS experiment_count
    FROM experiment_structure
    GROUP BY distinct_images
    ORDER BY distinct_images
    """
).df()

print(image_distribution.to_string(index=False))

print("\nEXAMPLES WITH MULTIPLE HEADLINES")
print("=" * 60)

examples = con.execute(
    """
    SELECT *
    FROM experiment_structure
    WHERE distinct_headlines > 1
    ORDER BY distinct_headlines DESC, package_count DESC
    LIMIT 10
    """
).df()

print(examples.to_string(index=False))

print("\nAnalysis complete. Source CSV was not modified.")

con.close()
