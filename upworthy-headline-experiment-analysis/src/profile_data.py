
from utils import get_connection, load_raw_view


def main():
    con = get_connection()

    try:
        load_raw_view(con, "upworthy")

        # 1. Overall performance
        print("\n=== 1. OVERALL PERFORMANCE ===")

        print(
            con.execute(
                """
                SELECT
                    COUNT(*) AS headline_variants,
                    COUNT(DISTINCT clickability_test_id)
                        AS experiments,
                    SUM(impressions) AS total_impressions,
                    SUM(clicks) AS total_clicks,
                    ROUND(
                        100.0 * SUM(clicks)
                        / NULLIF(SUM(impressions), 0),
                        4
                    ) AS overall_ctr_pct
                FROM upworthy
                """
            ).df().to_string(index=False)
        )

        # 2. Number of source rows per experiment
        print("\n=== 2. VARIANTS PER EXPERIMENT ===")

        print(
            con.execute(
                """
                WITH experiment_sizes AS (
                    SELECT
                        clickability_test_id,
                        COUNT(*) AS variants
                    FROM upworthy
                    GROUP BY clickability_test_id
                )
                SELECT
                    MIN(variants) AS min_variants,
                    MEDIAN(variants) AS median_variants,
                    ROUND(AVG(variants), 2) AS mean_variants,
                    MAX(variants) AS max_variants,
                    COUNT(*) AS experiments
                FROM experiment_sizes
                """
            ).df().to_string(index=False)
        )

        # 3. Distribution of experiment sizes
        print("\n=== 3. EXPERIMENT SIZE DISTRIBUTION ===")

        print(
            con.execute(
                """
                SELECT
                    variants,
                    COUNT(*) AS experiment_count
                FROM (
                    SELECT
                        clickability_test_id,
                        COUNT(*) AS variants
                    FROM upworthy
                    GROUP BY clickability_test_id
                ) AS experiment_sizes
                GROUP BY variants
                ORDER BY variants
                """
            ).df().to_string(index=False)
        )

        # 4. Basic data-quality checks
        print("\n=== 4. DATA QUALITY CHECKS ===")

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
                        WHERE impressions < 0 OR clicks < 0
                    ) AS negative_count_rows

                FROM upworthy
                """
            ).df().to_string(index=False)
        )

        # 5. Impression distribution
        print("\n=== 5. IMPRESSION DISTRIBUTION ===")

        print(
            con.execute(
                """
                SELECT
                    MIN(impressions) AS min_impressions,
                    MEDIAN(impressions) AS median_impressions,
                    ROUND(AVG(impressions), 2) AS mean_impressions,
                    MAX(impressions) AS max_impressions
                FROM upworthy
                """
            ).df().to_string(index=False)
        )

        print(
            "\nProfiling complete. Source CSV was not modified."
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()
