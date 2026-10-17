from utils import (
    EXPERIMENT_SUMMARY_FILE,
    COMPARISON_CANDIDATES_FILE,
    get_connection,
    load_parquet_view,
)


def main():
    if not EXPERIMENT_SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {EXPERIMENT_SUMMARY_FILE}"
        )

    COMPARISON_CANDIDATES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    con = get_connection()

    try:
        load_parquet_view(
            con,
            "experiment_summary",
            EXPERIMENT_SUMMARY_FILE,
        )

        candidates = con.sql("""
            SELECT
                *,
                CASE
                    WHEN distinct_image_ids = 0
                        THEN 'No recorded image ID'
                    WHEN distinct_headlines > 1
                         AND distinct_image_ids = 1
                        THEN 'Headline variation candidate'
                    WHEN distinct_headlines = 1
                         AND distinct_image_ids > 1
                        THEN 'Image variation candidate'
                    WHEN distinct_headlines > 1
                         AND distinct_image_ids > 1
                        THEN 'Mixed headline and image variation'
                    ELSE 'No recorded headline or image variation'
                END AS comparison_category
            FROM experiment_summary
        """)

        candidates.write_parquet(
            str(COMPARISON_CANDIDATES_FILE),
            compression="zstd",
        )

        print("\nCOMPARISON CANDIDATE CLASSIFICATION")
        print("=" * 70)

        print(
            con.execute("""
                SELECT
                    comparison_category,
                    COUNT(*) AS experiment_count,
                    ROUND(
                        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
                        2
                    ) AS percentage
                FROM read_parquet(?)
                GROUP BY comparison_category
                ORDER BY experiment_count DESC
            """, [str(COMPARISON_CANDIDATES_FILE)])
            .df()
            .to_string(index=False)
        )

        print("\nVALIDATION")
        print("=" * 70)

        print(
            con.execute("""
                SELECT
                    COUNT(*) AS total_experiments,
                    COUNT(DISTINCT clickability_test_id)
                        AS unique_experiment_ids,
                    SUM(package_count) AS total_packages
                FROM read_parquet(?)
            """, [str(COMPARISON_CANDIDATES_FILE)])
            .df()
            .to_string(index=False)
        )

        print(
            f"\nOutput saved to: {COMPARISON_CANDIDATES_FILE}"
        )
        print("\nSUCCESS: Comparison candidates classified.")

    finally:
        con.close()


if __name__ == "__main__":
    main()