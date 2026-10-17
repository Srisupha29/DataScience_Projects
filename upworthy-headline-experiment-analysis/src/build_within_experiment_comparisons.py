from utils import (
    PACKAGES_FILE,
    IMPRESSION_BALANCE_FILE,
    WITHIN_EXPERIMENT_FILE,
    get_connection,
    load_parquet_view,
)


def main():
    required_files = [
        PACKAGES_FILE,
        IMPRESSION_BALANCE_FILE,
    ]

    for file_path in required_files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )

    WITHIN_EXPERIMENT_FILE.parent.mkdir(
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

        load_parquet_view(
            con,
            "impression_balance",
            IMPRESSION_BALANCE_FILE,
        )

        comparisons = con.execute("""
            WITH experiment_baselines AS (
                SELECT
                    clickability_test_id AS experiment_id,
                    COUNT(*) AS source_row_count,
                    SUM(clicks) AS source_row_clicks,
                    SUM(impressions) AS source_row_impressions,
                    SUM(clicks)::DOUBLE
                        / NULLIF(SUM(impressions), 0)
                        AS experiment_baseline_ctr
                FROM packages
                GROUP BY clickability_test_id
            ),

            package_comparisons AS (
                SELECT
                    p.row_id,
                    p.package_id,
                    p.clickability_test_id AS experiment_id,
                    p.headline,
                    p.eyecatcher_id AS image_id,
                    p.created_at,
                    p.impressions,
                    p.clicks,
                    p.ctr AS package_ctr,
                    b.source_row_count,
                    b.source_row_clicks,
                    b.source_row_impressions,
                    b.experiment_baseline_ctr,

                    (
                        p.ctr - b.experiment_baseline_ctr
                    ) AS ctr_difference,

                    100.0 * (
                        p.ctr - b.experiment_baseline_ctr
                    ) / NULLIF(b.experiment_baseline_ctr, 0)
                        AS relative_ctr_difference_pct

                FROM packages AS p
                INNER JOIN experiment_baselines AS b
                    ON p.clickability_test_id = b.experiment_id
            )

            SELECT
                c.*,
                ib.max_min_impression_ratio,
                ib.impression_coefficient_of_variation,
                ib.balance_status,
                ib.randomization_risk_screen
            FROM package_comparisons AS c
            LEFT JOIN impression_balance AS ib
                ON c.experiment_id = ib.experiment_id
            ORDER BY
                c.experiment_id,
                c.created_at,
                c.row_id
        """).df()

        undefined_rows = comparisons[
            comparisons["relative_ctr_difference_pct"].isna()
        ]

        print("\nUNDEFINED RELATIVE CTR INVESTIGATION")
        print("=" * 60)

        if undefined_rows.empty:
            print("No undefined relative CTR comparisons found.")
        else:
            print(
                undefined_rows[
                    [
                        "experiment_id",
                        "row_id",
                        "headline",
                        "impressions",
                        "clicks",
                        "package_ctr",
                        "experiment_baseline_ctr",
                    ]
                ].to_string(index=False)
            )

            print("\nBaseline CTR values for affected experiments:")
            print(
                undefined_rows[
                    ["experiment_id", "experiment_baseline_ctr"]
                ]
                .drop_duplicates()
                .to_string(index=False)
            )

        con.register("comparison_results", comparisons)

        con.execute("""
            COPY comparison_results
            TO ?
            (FORMAT PARQUET, COMPRESSION ZSTD)
        """, [str(WITHIN_EXPERIMENT_FILE)])

        print("\nWITHIN-EXPERIMENT COMPARISON DATASET")
        print("=" * 60)
        print(f"Source rows: {len(comparisons):,}")
        print(
            "Unique source row IDs: "
            f"{comparisons['row_id'].nunique():,}"
        )
        print(
            "Unique experiments: "
            f"{comparisons['experiment_id'].nunique():,}"
        )
        print(
            "Rows with missing experiment baseline CTR: "
            f"{comparisons['experiment_baseline_ctr'].isna().sum():,}"
        )
        print(
            "Rows with undefined relative CTR difference: "
            f"{comparisons['relative_ctr_difference_pct'].isna().sum():,}"
        )

        print("\nEXAMPLE COMPARISONS")
        print("-" * 60)

        example_columns = [
            "experiment_id",
            "headline",
            "impressions",
            "clicks",
            "package_ctr",
            "experiment_baseline_ctr",
            "relative_ctr_difference_pct",
            "balance_status",
            "randomization_risk_screen",
        ]

        print(
            comparisons[example_columns]
            .head(10)
            .to_string(index=False)
        )

        print(f"\nSaved dataset: {WITHIN_EXPERIMENT_FILE}")

    finally:
        con.close()


if __name__ == "__main__":
    main()