from utils import (
    PACKAGES_FILE,
    IMPRESSION_BALANCE_FILE,
    get_connection,
    load_parquet_view,
)


# Flag exposure ratios at or above this threshold for investigation.
IMBALANCE_THRESHOLD = 1.5


def main():
    if not PACKAGES_FILE.exists():
        raise FileNotFoundError(
            f"Analytical dataset not found: {PACKAGES_FILE}"
        )

    IMPRESSION_BALANCE_FILE.parent.mkdir(
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

        balance = con.execute(
            """
            WITH experiment_metrics AS (
                SELECT
                    clickability_test_id AS experiment_id,
                    COUNT(*) AS row_count,
                    COUNT(DISTINCT package_id) AS distinct_package_ids,
                    SUM(impressions) AS total_row_impressions,
                    MIN(impressions) AS minimum_row_impressions,
                    MAX(impressions) AS maximum_row_impressions,
                    AVG(impressions) AS mean_row_impressions,
                    STDDEV_POP(impressions) AS sd_row_impressions,
                    MIN(created_at) AS first_record_at
                FROM packages
                GROUP BY clickability_test_id
            )
            SELECT
                *,
                maximum_row_impressions::DOUBLE
                    / NULLIF(minimum_row_impressions, 0)
                    AS max_min_impression_ratio,
                sd_row_impressions
                    / NULLIF(mean_row_impressions, 0)
                    AS impression_coefficient_of_variation,
                CASE
                    WHEN row_count < 2
                        THEN 'Insufficient distinct package rows'
                    WHEN maximum_row_impressions::DOUBLE
                        / NULLIF(minimum_row_impressions, 0)
                        >= ?
                        THEN 'Flag for exposure imbalance review'
                    ELSE 'Below review threshold'
                END AS balance_status,
                CASE
                    WHEN CAST(first_record_at AS DATE)
                        BETWEEN DATE '2013-06-25' AND DATE '2014-01-10'
                        THEN 'Within documented randomization-risk window'
                    ELSE 'Outside documented randomization-risk window'
                END AS randomization_risk_screen
            FROM experiment_metrics
            ORDER BY max_min_impression_ratio DESC NULLS LAST
            """,
            [IMBALANCE_THRESHOLD],
        ).df()

        con.register("balance_results", balance)

        con.execute(
            """
            COPY balance_results
            TO ?
            (FORMAT PARQUET, COMPRESSION ZSTD)
            """,
            [str(IMPRESSION_BALANCE_FILE)],
        )

        print("\nIMPRESSION BALANCE DIAGNOSTIC")
        print("=" * 60)
        print(f"Experiments evaluated: {len(balance):,}")
        print(f"Review threshold: {IMBALANCE_THRESHOLD:.2f}x")

        print("\nBALANCE STATUS COUNTS")
        print("-" * 60)
        print(
            balance["balance_status"]
            .value_counts(dropna=False)
            .to_string()
        )

        print("\nRANDOMIZATION-RISK SCREEN COUNTS")
        print("-" * 60)
        print(
            balance["randomization_risk_screen"]
            .value_counts(dropna=False)
            .to_string()
        )

        print("\nMOST IMBALANCED EXPERIMENTS")
        print("-" * 60)

        columns_to_show = [
            "experiment_id",
            "row_count",
            "distinct_package_ids",
            "minimum_row_impressions",
            "maximum_row_impressions",
            "max_min_impression_ratio",
            "impression_coefficient_of_variation",
            "balance_status",
            "first_record_at",
            "randomization_risk_screen",
        ]

        print(
            balance[columns_to_show]
            .head(10)
            .to_string(index=False)
        )

        print(
            f"\nSaved diagnostic dataset: {IMPRESSION_BALANCE_FILE}"
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()