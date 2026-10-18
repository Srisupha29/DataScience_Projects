from pathlib import Path
import duckdb
from utils import PROCESSED_DIR

CANDIDATES_FILE = PROCESSED_DIR / "comparison_candidates.parquet"
PACKAGES_FILE = PROCESSED_DIR / "packages.parquet"

OUTPUT_DIR = PROCESSED_DIR
COHORT_FILE = OUTPUT_DIR / "headline_cohort.parquet"
SUMMARY_FILE = OUTPUT_DIR / "headline_cohort_summary.csv"


def main():
    con = duckdb.connect()

    candidates = str(CANDIDATES_FILE)
    packages = str(PACKAGES_FILE)
    cohort = str(COHORT_FILE)
    summary = str(SUMMARY_FILE)

    con.execute(
        f"""
        COPY (
            SELECT p.*
            FROM read_parquet('{packages}') AS p
            INNER JOIN (
                SELECT clickability_test_id
                FROM read_parquet('{candidates}')
                WHERE distinct_headlines > 1
                  AND distinct_image_ids = 1
                  AND has_missing_image_id = FALSE
            ) AS eligible
            USING (clickability_test_id)
        )
        TO '{cohort}' (FORMAT PARQUET)
        """
    )

    con.execute(
        f"""
        COPY (
            SELECT
                COUNT(DISTINCT clickability_test_id)
                    AS eligible_experiments,
                COUNT(*) AS package_rows,
                COUNT(DISTINCT package_id)
                    AS distinct_package_ids,
                SUM(impressions) AS total_impressions,
                SUM(clicks) AS total_clicks,
                SUM(clicks) / NULLIF(SUM(impressions), 0)
                    AS pooled_ctr
            FROM read_parquet('{cohort}')
        )
        TO '{summary}' (HEADER, DELIMITER ',')
        """
    )

    print("Headline cohort created.")
    print(f"Packages: {COHORT_FILE}")
    print(f"Summary:  {SUMMARY_FILE}")

    print(
        con.execute(
            f"""
            SELECT *
            FROM read_csv_auto('{summary}')
            """
        ).fetchdf().to_string(index=False)
    )

    con.close()


if __name__ == "__main__":
    main()
