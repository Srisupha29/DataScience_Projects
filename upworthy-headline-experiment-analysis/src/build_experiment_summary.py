from pathlib import Path
import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_DIR / "data" / "processed" / "packages.parquet"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "experiment_summary.parquet"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT_FILE}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(database=":memory:")

    try:
        packages = con.read_parquet(str(INPUT_FILE))
        packages.create_view("packages")

        # Summarize packages within each experiment.
        summary = con.sql("""
            SELECT
                clickability_test_id,
                COUNT(*) AS package_count,
                COUNT(DISTINCT headline) AS distinct_headlines,
                COUNT(DISTINCT eyecatcher_id) AS distinct_image_ids,
                COUNT(*) FILTER (
                    WHERE eyecatcher_id IS NULL
                ) AS missing_image_id_packages,
                SUM(impressions) AS total_impressions,
                SUM(clicks) AS total_clicks,
                SUM(clicks)::DOUBLE
                    / NULLIF(SUM(impressions), 0) AS pooled_ctr,
                MIN(ctr) AS minimum_package_ctr,
                MAX(ctr) AS maximum_package_ctr
            FROM packages
            GROUP BY clickability_test_id
        """)

        summary.write_parquet(
            str(OUTPUT_FILE),
            compression="zstd",
        )

        # Verify the exported summary.
        result = con.execute("""
            SELECT
                COUNT(*) AS total_experiments,
                SUM(package_count) AS total_packages,
                COUNT(*) FILTER (
                    WHERE distinct_headlines > 1
                ) AS experiments_with_multiple_headlines,
                COUNT(*) FILTER (
                    WHERE distinct_image_ids > 1
                ) AS experiments_with_multiple_image_ids,
                COUNT(*) FILTER (
                    WHERE missing_image_id_packages > 0
                ) AS experiments_with_missing_image_ids,
                COUNT(*) FILTER (
                    WHERE pooled_ctr IS NULL
                ) AS experiments_with_null_pooled_ctr
            FROM read_parquet(?)
        """, [str(OUTPUT_FILE)]).df()

        print("\nEXPERIMENT SUMMARY VALIDATION")
        print("=" * 60)
        print(result.to_string(index=False))

        print("\nSAMPLE EXPERIMENTS")
        print("=" * 60)
        print(con.execute("""
            SELECT *
            FROM read_parquet(?)
            ORDER BY package_count DESC
            LIMIT 5
        """, [str(OUTPUT_FILE)]).df().to_string(index=False))

        total = result.iloc[0]

        if total["total_experiments"] != 4873:
            raise ValueError("Unexpected experiment count.")

        if total["total_packages"] != 22666:
            raise ValueError("Package count does not match the source.")

        if total["experiments_with_null_pooled_ctr"] != 0:
            raise ValueError("Some experiments have a null pooled CTR.")

        print(f"\nOutput saved to: {OUTPUT_FILE}")
        print("\nSUCCESS: Experiment summary validated.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
