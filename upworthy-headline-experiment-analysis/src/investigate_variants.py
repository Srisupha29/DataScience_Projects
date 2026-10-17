from utils import (
    RAW_FILE,
    get_connection,
    load_raw_view,
)


EXPERIMENT_IDS = [
    "53480581be4154443a000008",
    "52930ef6d40ad9e426003b53",
]


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source CSV not found: {RAW_FILE}"
        )

    con = get_connection()

    try:
        load_raw_view(con, "upworthy")

        for experiment_id in EXPERIMENT_IDS:
            print(f"\n{'=' * 80}")
            print(f"EXPERIMENT: {experiment_id}")
            print("=" * 80)

            result = con.execute(
                """
                SELECT
                    column00,
                    headline,
                    slug,
                    eyecatcher_id,
                    impressions,
                    clicks,
                    ROUND(
                        100.0 * clicks / NULLIF(impressions, 0),
                        4
                    ) AS ctr_pct,
                    significance,
                    first_place,
                    winner
                FROM upworthy
                WHERE clickability_test_id = ?
                ORDER BY slug
                """,
                [experiment_id],
            ).df()

            print(result.to_string(index=False))

            print("\nDistinct values within this experiment:")

            summary = con.execute(
                """
                SELECT
                    COUNT(*) AS row_count,
                    COUNT(DISTINCT headline)
                        AS distinct_headlines,
                    COUNT(DISTINCT slug) AS distinct_slugs,
                    COUNT(DISTINCT eyecatcher_id)
                        AS distinct_image_ids,
                    COUNT(DISTINCT impressions)
                        AS distinct_impression_counts,
                    COUNT(DISTINCT clicks)
                        AS distinct_click_counts
                FROM upworthy
                WHERE clickability_test_id = ?
                """,
                [experiment_id],
            ).df()

            print(summary.to_string(index=False))

        print(
            "\nInvestigation complete. "
            "Source CSV was not modified."
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()