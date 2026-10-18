
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
                    COUNT(DISTINCT package_id) AS distinct_package_ids,
                    SUM(clicks) AS experiment_total_clicks,
                    SUM(impressions) AS experiment_total_impressions,
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
                    p.normalized_headline,
                    p.eyecatcher_id AS image_id,
                    p.created_at,
                    p.impressions,
                    p.clicks,
                    p.ctr AS package_ctr,

                    b.source_row_count,
                    b.distinct_package_ids,
                    b.experiment_total_clicks,
                    b.experiment_total_impressions,
                    b.experiment_baseline_ctr,

                    b.experiment_total_clicks - p.clicks
                        AS rest_of_experiment_clicks,

                    b.experiment_total_impressions - p.impressions
                        AS rest_of_experiment_impressions,

                    (
                        b.experiment_total_clicks - p.clicks
                    )::DOUBLE
                    / NULLIF(
                        b.experiment_total_impressions - p.impressions,
                        0
                    ) AS rest_of_experiment_ctr,

                    (
                        p.ctr -
                        (
                            b.experiment_total_clicks - p.clicks
                        )::DOUBLE
                        / NULLIF(
                            b.experiment_total_impressions - p.impressions,
                            0
                        )
                    ) AS ctr_difference_vs_rest,

                    100.0 * (
                        p.ctr -
                        (
                            b.experiment_total_clicks - p.clicks
                        )::DOUBLE
                        / NULLIF(
                            b.experiment_total_impressions - p.impressions,
                            0
                        )
                    ) / NULLIF(
                        (
                            b.experiment_total_clicks - p.clicks
                        )::DOUBLE
                        / NULLIF(
                            b.experiment_total_impressions - p.impressions,
                            0
                        ),
                        0
                    ) AS relative_ctr_difference_vs_rest_pct,

                    CASE
                        WHEN b.experiment_total_clicks = 0
                            THEN TRUE
                        ELSE FALSE
                    END AS zero_click_experiment,

                    CASE
                        WHEN b.experiment_total_clicks = 0
                            THEN 'Zero-click experiment'
                        WHEN b.source_row_count <= 1
                            THEN 'No other source rows to compare'
                        WHEN b.experiment_total_impressions - p.impressions <= 0
                            THEN 'No remaining impressions'
                        WHEN b.experiment_total_clicks - p.clicks = 0
                            THEN 'Rest-of-experiment CTR is zero'
                        WHEN b.experiment_total_clicks = 0
                            THEN 'Zero-click experiment'
                        ELSE 'Relative CTR difference defined'
                    END AS comparison_status

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
            "Rows with undefined rest-of-experiment CTR: "
            f"{comparisons['rest_of_experiment_ctr'].isna().sum():,}"
        )
        print(
            "Rows with undefined relative CTR difference: "
            f"{comparisons['relative_ctr_difference_vs_rest_pct'].isna().sum():,}"
        )
        print(
            "Zero-click experiments: "
            f"{comparisons.loc[
                comparisons['zero_click_experiment'],
                'experiment_id'
            ].nunique():,}"
        )

        print("\nCOMPARISON STATUS COUNTS")
        print("-" * 60)
        print(
            comparisons["comparison_status"]
            .value_counts(dropna=False)
            .to_string()
        )

        print("\nEXAMPLE COMPARISONS")
        print("-" * 60)

        example_columns = [
            "experiment_id",
            "normalized_headline",
            "package_id",
            "impressions",
            "clicks",
            "package_ctr",
            "rest_of_experiment_ctr",
            "ctr_difference_vs_rest",
            "relative_ctr_difference_vs_rest_pct",
            "zero_click_experiment",
            "comparison_status",
        ]

        print(
            comparisons[example_columns]
            .head(10)
            .to_string(index=False)
        )

        print(f"\nSaved dataset: {WITHIN_EXPERIMENT_FILE}")

        print(
            "\nInterpretation note: comparisons are descriptive "
            "source-row comparisons, not independent variant-level "
            "estimates or statistical significance tests."
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()
