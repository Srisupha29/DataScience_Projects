from utils import (
    PACKAGES_FILE,
    get_connection,
    load_parquet_view,
)


def main():
    if not PACKAGES_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {PACKAGES_FILE}"
        )

    con = get_connection()

    try:
        load_parquet_view(
            con,
            "packages",
            PACKAGES_FILE,
        )

        # Count how often each stimulus identity appears.
        repetition_summary = con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT package_id) AS distinct_package_ids,
                COUNT(*) - COUNT(DISTINCT package_id)
                    AS rows_beyond_first_occurrence,
                COUNT(*) FILTER (
                    WHERE eyecatcher_id IS NULL
                ) AS rows_missing_image_id
            FROM packages
        """).df()

        print("\nREPETITION SUMMARY")
        print("=" * 70)
        print(repetition_summary.to_string(index=False))

        # Examine repeated identities and their exposure counts.
        repeated = con.execute("""
            SELECT
                package_id,
                clickability_test_id,
                headline,
                eyecatcher_id,
                COUNT(*) AS source_rows,
                COUNT(DISTINCT impressions)
                    AS distinct_impression_counts,
                COUNT(DISTINCT clicks) AS distinct_click_counts,
                MIN(impressions) AS min_impressions,
                MAX(impressions) AS max_impressions,
                MIN(clicks) AS min_clicks,
                MAX(clicks) AS max_clicks
            FROM packages
            GROUP BY
                package_id,
                clickability_test_id,
                headline,
                eyecatcher_id
            HAVING COUNT(*) > 1
            ORDER BY source_rows DESC
            LIMIT 20
        """).df()

        print("\nREPEATED STIMULUS IDENTITIES")
        print("=" * 70)

        if repeated.empty:
            print("No repeated identities found.")
        else:
            print(repeated.to_string(index=False))

        # Check whether performance counts are identical
        # within each repeated identity.
        consistency = con.execute("""
            WITH grouped AS (
                SELECT
                    package_id,
                    COUNT(*) AS source_rows,
                    COUNT(DISTINCT impressions)
                        AS impression_values,
                    COUNT(DISTINCT clicks) AS click_values
                FROM packages
                GROUP BY package_id
                HAVING COUNT(*) > 1
            )
            SELECT
                COUNT(*) AS repeated_identities,
                COUNT(*) FILTER (
                    WHERE impression_values = 1
                      AND click_values = 1
                ) AS identical_count_identities,
                COUNT(*) FILTER (
                    WHERE impression_values > 1
                       OR click_values > 1
                ) AS differing_count_identities
            FROM grouped
        """).df()

        print("\nCOUNT CONSISTENCY")
        print("=" * 70)
        print(consistency.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    main()