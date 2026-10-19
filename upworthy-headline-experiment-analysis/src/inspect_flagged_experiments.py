from utils import (
    PACKAGES_FILE,
    get_connection,
    load_parquet_view,
)

FLAGGED_EXPERIMENTS = [
    "5348bd88fe9c5a1bf500001b",
    "526d4c1c94d1f182f600574f",
    "52a5cf335de7b1f7a3000e04",
    "51ddbd415d8e6fa6d2006471",
    "51d1e3934a5d3ff28b0001b0",
]

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

        print("\nFLAGGED EXPERIMENT RECORDS")
        print("=" * 100)

        results = con.execute("""
            SELECT
                clickability_test_id AS experiment_id,
                package_id,
                normalized_headline,
                eyecatcher_id,
                created_at,
                impressions,
                clicks,
                ctr,
                COUNT(*) OVER (
                    PARTITION BY
                        clickability_test_id,
                        package_id
                ) AS package_record_count
            FROM packages
            WHERE clickability_test_id IN (
                SELECT UNNEST(?)
            )
            ORDER BY
                experiment_id,
                package_id,
                created_at
        """, [FLAGGED_EXPERIMENTS]).df()

        print(results.to_string(index=False))

        print("\nSUMMARY BY EXPERIMENT")
        print("=" * 100)

        summary = con.execute("""
            SELECT
                clickability_test_id AS experiment_id,
                COUNT(*) AS source_rows,
                COUNT(DISTINCT package_id)
                    AS distinct_package_ids,
                COUNT(DISTINCT normalized_headline)
                    AS distinct_headlines,
                COUNT(DISTINCT eyecatcher_id)
                    AS distinct_image_ids,
                COUNT(*) FILTER (
                    WHERE eyecatcher_id IS NULL
                       OR trim(eyecatcher_id) = ''
                ) AS missing_image_id_rows,
                COUNT(*) FILTER (
                    WHERE package_id IS NULL
                ) AS missing_package_id_rows,
                MIN(created_at) AS first_record,
                MAX(created_at) AS last_record
            FROM packages
            WHERE clickability_test_id IN (
                SELECT UNNEST(?)
            )
            GROUP BY clickability_test_id
            ORDER BY clickability_test_id
        """, [FLAGGED_EXPERIMENTS]).df()

        print(summary.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    main()
