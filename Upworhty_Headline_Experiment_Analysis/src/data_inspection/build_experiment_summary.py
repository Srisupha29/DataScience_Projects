
from utils.utils import (
    PACKAGES_FILE,
    EXPERIMENT_SUMMARY_FILE,
    EXPECTED_PACKAGE_ROWS,
    EXPECTED_EXPERIMENTS,
    get_connection,
    load_parquet_view,
)


def main():
    if not PACKAGES_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {PACKAGES_FILE}"
        )

    EXPERIMENT_SUMMARY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    con = get_connection()

    try:
        load_parquet_view(
            con,
            "packages",
            PACKAGES_FILE,
        )

        # Summarize source rows within each experiment.
        # Headline counts use the normalized headline column.
        summary = con.sql("""
            SELECT
                clickability_test_id,
                COUNT(*) AS package_count,
                COUNT(DISTINCT normalized_headline)
                    AS distinct_headlines,
                COUNT(DISTINCT package_id)
                    AS distinct_package_ids,
                COUNT(DISTINCT eyecatcher_id)
                    AS distinct_image_ids,
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
            str(EXPERIMENT_SUMMARY_FILE),
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
                    WHERE distinct_package_ids > 1
                ) AS experiments_with_multiple_package_ids,
                COUNT(*) FILTER (
                    WHERE missing_image_id_packages > 0
                ) AS experiments_with_missing_image_ids,
                COUNT(*) FILTER (
                    WHERE pooled_ctr IS NULL
                ) AS experiments_with_null_pooled_ctr
            FROM read_parquet(?)
        """, [str(EXPERIMENT_SUMMARY_FILE)]).df()

        print("\nEXPERIMENT SUMMARY VALIDATION")
        print("=" * 60)
        print(result.to_string(index=False))

        print("\nSAMPLE EXPERIMENTS")
        print("=" * 60)
        print(
            con.execute("""
                SELECT *
                FROM read_parquet(?)
                ORDER BY package_count DESC
                LIMIT 5
            """, [str(EXPERIMENT_SUMMARY_FILE)])
            .df()
            .to_string(index=False)
        )

        total = result.iloc[0]

        if total["total_experiments"] != EXPECTED_EXPERIMENTS:
            raise ValueError(
                "Unexpected experiment count: "
                f"{total['total_experiments']:,}; "
                f"expected {EXPECTED_EXPERIMENTS:,}."
            )

        if total["total_packages"] != EXPECTED_PACKAGE_ROWS:
            raise ValueError(
                "Source-row count does not match the expected count: "
                f"{total['total_packages']:,}; "
                f"expected {EXPECTED_PACKAGE_ROWS:,}."
            )

        if total["experiments_with_null_pooled_ctr"] != 0:
            raise ValueError(
                "Some experiments have a null pooled CTR."
            )

        print(f"\nOutput saved to: {EXPERIMENT_SUMMARY_FILE}")
        print("\nSUCCESS: Experiment summary validated.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
