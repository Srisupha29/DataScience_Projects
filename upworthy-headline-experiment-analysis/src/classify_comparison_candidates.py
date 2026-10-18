
from utils import (
    EXPERIMENT_SUMMARY_FILE,
    COMPARISON_CANDIDATES_FILE,
    EXPECTED_PACKAGE_ROWS,
    EXPECTED_EXPERIMENTS,
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

        # distinct_headlines is already calculated using
        # normalized_headline in build_experiment_summary.py.
        # Categories identify potential comparisons, not proof
        # that only one experimental variable changed.
        candidates = con.sql("""
            SELECT
                *,
                missing_image_id_packages > 0
                    AS has_missing_image_id,
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

        category_results = con.execute("""
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
        """, [str(COMPARISON_CANDIDATES_FILE)]).df()

        print(category_results.to_string(index=False))

        print("\nVALIDATION")
        print("=" * 70)

        result = con.execute("""
            SELECT
                COUNT(*) AS total_experiments,
                COUNT(DISTINCT clickability_test_id)
                    AS unique_experiment_ids,
                SUM(package_count) AS total_source_rows,
                COUNT(*) FILTER (
                    WHERE has_missing_image_id
                ) AS experiments_with_missing_image_ids,
                COUNT(*) FILTER (
                    WHERE comparison_category =
                        'Headline variation candidate'
                ) AS headline_variation_candidates,
                COUNT(*) FILTER (
                    WHERE comparison_category =
                        'Image variation candidate'
                ) AS image_variation_candidates,
                COUNT(*) FILTER (
                    WHERE comparison_category =
                        'Mixed headline and image variation'
                ) AS mixed_variation_candidates
            FROM read_parquet(?)
        """, [str(COMPARISON_CANDIDATES_FILE)]).df()

        print(result.to_string(index=False))

        totals = result.iloc[0]

        if totals["total_experiments"] != EXPECTED_EXPERIMENTS:
            raise ValueError(
                "Unexpected experiment count: "
                f"{totals['total_experiments']:,}; "
                f"expected {EXPECTED_EXPERIMENTS:,}."
            )

        if totals["unique_experiment_ids"] != EXPECTED_EXPERIMENTS:
            raise ValueError(
                "Experiment IDs are not unique in the output."
            )

        if totals["total_source_rows"] != EXPECTED_PACKAGE_ROWS:
            raise ValueError(
                "Unexpected source-row total: "
                f"{totals['total_source_rows']:,}; "
                f"expected {EXPECTED_PACKAGE_ROWS:,}."
            )

        print(
            f"\nOutput saved to: {COMPARISON_CANDIDATES_FILE}"
        )
        print("\nSUCCESS: Comparison candidates classified and validated.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
