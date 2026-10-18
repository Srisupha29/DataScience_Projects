
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
                    COUNT(*) AS source_rows,
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
        print("\n=== 2. SOURCE ROWS PER EXPERIMENT ===")

        print(
            con.execute(
                """
                WITH experiment_sizes AS (
                    SELECT
                        clickability_test_id,
                        COUNT(*) AS source_rows
                    FROM upworthy
                    GROUP BY clickability_test_id
                )
                SELECT
                    MIN(source_rows) AS min_source_rows,
                    MEDIAN(source_rows) AS median_source_rows,
                    ROUND(AVG(source_rows), 2) AS mean_source_rows,
                    MAX(source_rows) AS max_source_rows,
                    COUNT(*) AS experiments
                FROM experiment_sizes
                """
            ).df().to_string(index=False)
        )

        # 3. Distribution of experiment sizes
        print("\n=== 3. SOURCE ROW COUNT DISTRIBUTION ===")

        print(
            con.execute(
                """
                SELECT
                    source_rows,
                    COUNT(*) AS experiment_count
                FROM (
                    SELECT
                        clickability_test_id,
                        COUNT(*) AS source_rows
                    FROM upworthy
                    GROUP BY clickability_test_id
                ) AS experiment_sizes
                GROUP BY source_rows
                ORDER BY source_rows
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
