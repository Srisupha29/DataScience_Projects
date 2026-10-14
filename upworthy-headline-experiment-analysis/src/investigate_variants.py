
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

experiment_ids = [
    "53480581be4154443a000008",
    "52930ef6d40ad9e426003b53",
]

for experiment_id in experiment_ids:
    print(f"\n{'=' * 80}")
    print(f"EXPERIMENT: {experiment_id}")
    print("=" * 80)

    result = con.execute(
        """
        SELECT
            column00,
            headline,
            slug,
            eyecatcher_id,
            impressions,
            clicks,
            ROUND(
                100.0 * clicks / NULLIF(impressions, 0),
                4
            ) AS ctr_pct,
            significance,
            first_place,
            winner
        FROM upworthy
        WHERE clickability_test_id = ?
        ORDER BY slug
        """,
        [experiment_id],
    ).df()

    print(result.to_string(index=False))

    print("\nDistinct values within this experiment:")

    summary = con.execute(
        """
        SELECT
            COUNT(*) AS row_count,
            COUNT(DISTINCT headline) AS distinct_headlines,
            COUNT(DISTINCT slug) AS distinct_slugs,
            COUNT(DISTINCT eyecatcher_id) AS distinct_image_ids,
            COUNT(DISTINCT impressions) AS distinct_impression_counts,
            COUNT(DISTINCT clicks) AS distinct_click_counts
        FROM upworthy
        WHERE clickability_test_id = ?
        """,
        [experiment_id],
    ).df()

    print(summary.to_string(index=False))

print("\nInvestigation complete. Source CSV was not modified.")

con.close()
