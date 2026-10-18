from utils import get_connection, load_raw_view


def main():
    con = get_connection()
    try:
        load_raw_view(con, "upworthy")
        con.execute("""
            CREATE TEMP VIEW experiment_structure AS
            SELECT
                clickability_test_id,
                COUNT(*) AS package_count,
                COUNT(DISTINCT headline) AS distinct_headlines,
                COUNT(DISTINCT eyecatcher_id) AS distinct_images,
                COUNT(*) FILTER (WHERE eyecatcher_id IS NULL)
                    AS missing_image_id_rows
            FROM upworthy
            GROUP BY clickability_test_id
        """)

        print("HEADLINE × IMAGE VARIATION")
        print("=" * 65)
        print(con.execute("""
            SELECT
                CASE WHEN distinct_headlines = 1
                    THEN 'One headline' ELSE 'Multiple headlines'
                END AS headline_pattern,
                CASE
                    WHEN missing_image_id_rows = package_count
                        THEN 'All image IDs missing'
                    WHEN distinct_images = 1
                        THEN 'One distinct image ID'
                    WHEN distinct_images > 1
                        THEN 'Multiple distinct image IDs'
                    ELSE 'Some image IDs missing; none identified'
                END AS image_pattern,
                COUNT(*) AS experiment_count
            FROM experiment_structure
            GROUP BY headline_pattern, image_pattern
            ORDER BY headline_pattern, image_pattern
        """).df().to_string(index=False))

        print("\nIMAGE ID COMPLETENESS")
        print("=" * 65)
        print(con.execute("""
            SELECT
                COUNT(*) AS total_experiments,
                COUNT(*) FILTER (WHERE missing_image_id_rows = 0)
                    AS experiments_with_no_missing_image_ids,
                COUNT(*) FILTER (
                    WHERE missing_image_id_rows > 0
                      AND missing_image_id_rows < package_count
                ) AS experiments_with_some_missing_image_ids,
                COUNT(*) FILTER (WHERE missing_image_id_rows = package_count)
                    AS experiments_with_all_image_ids_missing,
                SUM(missing_image_id_rows) AS total_rows_missing_image_id
            FROM experiment_structure
        """).df().to_string(index=False))

        # Candidate classification is structural only; it does not claim
        # that an experiment was randomized or supports causal inference.
        print("\nEXPERIMENT ELIGIBILITY COUNTS")
        print("=" * 65)
        print(con.execute("""
            SELECT
                COUNT(*) AS total_experiments,
                COUNT(*) FILTER (WHERE distinct_headlines > 1)
                    AS multiple_headlines,
                COUNT(*) FILTER (WHERE distinct_headlines > 1
                                  AND distinct_images = 1
                                  AND missing_image_id_rows = 0)
                    AS headline_comparison_candidates,
                COUNT(*) FILTER (WHERE distinct_headlines > 1
                                  AND distinct_images > 1)
                    AS headline_and_image_variation,
                COUNT(*) FILTER (WHERE distinct_headlines = 1)
                    AS no_headline_variant
            FROM experiment_structure
        """).df().to_string(index=False))
        print("\nClassification complete. Source CSV was not modified.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
