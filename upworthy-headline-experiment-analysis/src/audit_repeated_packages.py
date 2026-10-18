from utils import PACKAGES_FILE, get_connection, load_parquet_view


def main():
    if not PACKAGES_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {PACKAGES_FILE}")

    con = get_connection()
    try:
        load_parquet_view(con, "packages", PACKAGES_FILE)

        print("\nREPETITION SUMMARY")
        print("=" * 70)
        print(con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT package_id) AS distinct_package_ids,
                COUNT(*) - COUNT(DISTINCT package_id) AS rows_beyond_first_occurrence,
                COUNT(*) FILTER (WHERE eyecatcher_id IS NULL) AS rows_missing_image_id
            FROM packages
        """).df().to_string(index=False))

        print("\nREPEATED PACKAGE IDENTITIES AND METRICS")
        print("=" * 70)
        print(con.execute("""
            SELECT
                package_id, clickability_test_id, headline, eyecatcher_id,
                COUNT(*) AS source_rows,
                COUNT(DISTINCT impressions) AS distinct_impression_counts,
                COUNT(DISTINCT clicks) AS distinct_click_counts,
                MIN(impressions) AS min_impressions,
                MAX(impressions) AS max_impressions,
                MIN(clicks) AS min_clicks,
                MAX(clicks) AS max_clicks
            FROM packages
            GROUP BY package_id, clickability_test_id, headline, eyecatcher_id
            HAVING COUNT(*) > 1
            ORDER BY source_rows DESC
            LIMIT 20
        """).df().to_string(index=False))

        print("\nREPEATED IDENTITY COUNT CONSISTENCY")
        print("=" * 70)
        print(con.execute("""
            WITH grouped AS (
                SELECT package_id,
                       COUNT(*) AS source_rows,
                       COUNT(DISTINCT impressions) AS impression_values,
                       COUNT(DISTINCT clicks) AS click_values
                FROM packages
                GROUP BY package_id
                HAVING COUNT(*) > 1
            )
            SELECT
                COUNT(*) AS repeated_identities,
                COUNT(*) FILTER (
                    WHERE impression_values = 1 AND click_values = 1
                ) AS identical_count_identities,
                COUNT(*) FILTER (
                    WHERE impression_values > 1 OR click_values > 1
                ) AS differing_count_identities
            FROM grouped
        """).df().to_string(index=False))

        print("\nTIMESTAMP CONSISTENCY")
        print("=" * 70)
        print(con.execute("""
            SELECT
                COUNT(*) AS repeated_identities,
                COUNT(*) FILTER (WHERE distinct_timestamps = 1) AS one_timestamp,
                COUNT(*) FILTER (WHERE distinct_timestamps > 1) AS multiple_timestamps,
                COUNT(*) FILTER (WHERE missing_timestamps > 0)
                    AS identities_with_missing_timestamps
            FROM (
                SELECT package_id,
                       COUNT(DISTINCT created_at) AS distinct_timestamps,
                       COUNT(*) FILTER (WHERE created_at IS NULL) AS missing_timestamps
                FROM packages
                GROUP BY package_id
                HAVING COUNT(*) > 1
            ) repeated
        """).df().to_string(index=False))

        print("\nEXAMPLE SOURCE ROWS")
        print("=" * 70)
        print(con.execute("""
            SELECT package_id, created_at, impressions, clicks, row_id
            FROM packages
            WHERE package_id IN (
                SELECT package_id FROM packages
                GROUP BY package_id HAVING COUNT(*) > 1
            )
            ORDER BY package_id, created_at
            LIMIT 20
        """).df().to_string(index=False))

        print("\nAudit complete. No dataset was modified.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
