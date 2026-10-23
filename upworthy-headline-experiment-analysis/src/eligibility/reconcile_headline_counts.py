from utils.utils import get_connection, load_raw_view

def main():
    con = get_connection()

    try:
        load_raw_view(con, "upworthy")

        results = con.execute("""
            WITH headline_counts AS (
                SELECT
                    clickability_test_id,
                    COUNT(DISTINCT headline) AS original_headlines,
                    COUNT(DISTINCT LOWER(TRIM(headline)))
                        AS normalized_headlines,
                    COUNT(*) AS package_count
                FROM upworthy
                GROUP BY clickability_test_id
            )
            SELECT
                COUNT(*) AS total_experiments,

                COUNT(*) FILTER (
                    WHERE original_headlines > 1
                ) AS experiments_with_multiple_original_headlines,

                COUNT(*) FILTER (
                    WHERE normalized_headlines > 1
                ) AS experiments_with_multiple_normalized_headlines,

                COUNT(*) FILTER (
                    WHERE original_headlines > 1
                      AND normalized_headlines = 1
                ) AS experiments_reclassified_by_normalization,

                COUNT(*) FILTER (
                    WHERE original_headlines != normalized_headlines
                ) AS experiments_with_different_headline_counts
            FROM headline_counts
        """).df()

        print("\nHEADLINE COUNT RECONCILIATION")
        print("=" * 65)
        print(results.to_string(index=False))

        print("\nEXPERIMENTS CHANGED BY NORMALIZATION")
        print("=" * 65)

        changed = con.execute("""
            WITH headline_counts AS (
                SELECT
                    clickability_test_id,
                    COUNT(DISTINCT headline) AS original_headlines,
                    COUNT(DISTINCT LOWER(TRIM(headline)))
                        AS normalized_headlines
                FROM upworthy
                GROUP BY clickability_test_id
            )
            SELECT *
            FROM headline_counts
            WHERE original_headlines != normalized_headlines
            ORDER BY
                original_headlines - normalized_headlines DESC,
                clickability_test_id
            LIMIT 30
        """).df()

        print(changed.to_string(index=False))

        print("\nCOMPARISON WITH PROCESSED DATASETS")
        print("=" * 65)

        processed = con.execute("""
            WITH raw_counts AS (
                SELECT
                    clickability_test_id,
                    COUNT(DISTINCT LOWER(TRIM(headline)))
                        AS raw_normalized_headlines
                FROM upworthy
                GROUP BY clickability_test_id
            )
            SELECT
                r.clickability_test_id,
                r.raw_normalized_headlines,
                s.distinct_headlines AS summary_headlines,
                c.comparison_category
            FROM raw_counts r
            LEFT JOIN read_parquet(
                'data/processed/experiment_summary.parquet'
            ) s USING (clickability_test_id)
            LEFT JOIN read_parquet(
                'data/processed/comparison_candidates.parquet'
            ) c USING (clickability_test_id)
            WHERE r.raw_normalized_headlines
                != s.distinct_headlines
            ORDER BY r.clickability_test_id
        """).df()

        print(processed.to_string(index=False))

        print("\nPROCESSED CATEGORY COUNTS")
        print("=" * 65)

        categories = con.execute("""
            SELECT
                comparison_category,
                COUNT(*) AS experiment_count
            FROM read_parquet(
                'data/processed/comparison_candidates.parquet'
            )
            GROUP BY comparison_category
            ORDER BY comparison_category
        """).df()

        print(categories.to_string(index=False))

        print("\nMULTIPLE HEADLINES WITH NO RECORDED IMAGE IDs")
        print("=" * 65)

        affected = con.execute("""
            SELECT
                clickability_test_id,
                package_count,
                distinct_headlines,
                distinct_image_ids,
                missing_image_id_packages
            FROM read_parquet(
                'data/processed/experiment_summary.parquet'
            )
            WHERE distinct_headlines > 1
              AND distinct_image_ids = 0
            ORDER BY clickability_test_id
        """).df()

        print(affected.to_string(index=False))
        print(f"\nAffected experiments: {len(affected)}")

        print("\nALL EXPERIMENTS WITH NO RECORDED IMAGE IDs")
        print("=" * 65)

        no_image_ids = con.execute("""
            SELECT
                clickability_test_id,
                package_count,
                distinct_headlines,
                distinct_image_ids,
                missing_image_id_packages
            FROM read_parquet(
                'data/processed/experiment_summary.parquet'
            )
            WHERE distinct_image_ids = 0
            ORDER BY clickability_test_id
        """).df()

        print(no_image_ids.to_string(index=False))
        print(f"\nAffected experiments: {len(no_image_ids)}")

    finally:
        con.close()


if __name__ == "__main__":
    main()
