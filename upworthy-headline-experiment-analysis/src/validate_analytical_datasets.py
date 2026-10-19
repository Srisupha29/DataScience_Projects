
from utils import (
    PACKAGES_FILE,
    EDITORIAL_FILE,
    EXPERIMENT_SUMMARY_FILE,
    COMPARISON_CANDIDATES_FILE,
    IMPRESSION_BALANCE_FILE,
    WITHIN_EXPERIMENT_FILE,
    EXPECTED_PACKAGE_ROWS,
    EXPECTED_EXPERIMENTS,
    get_connection,
    load_parquet_view,
)


def main():
    datasets = [
        ("packages", PACKAGES_FILE),
        ("editorial_metadata", EDITORIAL_FILE),
        ("experiment_summary", EXPERIMENT_SUMMARY_FILE),
        ("comparison_candidates", COMPARISON_CANDIDATES_FILE),
        ("impression_balance", IMPRESSION_BALANCE_FILE),
        ("within_experiment_comparisons", WITHIN_EXPERIMENT_FILE),
    ]

    for _, file_path in datasets:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )

    con = get_connection()
    checks = []

    def record_check(name, passed, details):
        checks.append({
            "check": name,
            "status": "PASS" if passed else "FAIL",
            "details": str(details),
        })

    try:
        for view_name, file_path in datasets:
            load_parquet_view(con, view_name, file_path)

        # 1. Package row counts and CTR integrity.
        result = con.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT clickability_test_id),
                COUNT(*) FILTER (WHERE ctr IS NULL),
                COUNT(*) FILTER (
                    WHERE ABS(
                        ctr - clicks::DOUBLE
                        / NULLIF(impressions, 0)
                    ) > 1e-12
                )
            FROM packages
        """).fetchone()

        record_check(
            "Package dataset",
            result[0] == EXPECTED_PACKAGE_ROWS
            and result[1] == EXPECTED_EXPERIMENTS
            and result[2] == 0
            and result[3] == 0,
            f"rows={result[0]}, experiments={result[1]}, "
            f"null CTR={result[2]}, incorrect CTR={result[3]}",
        )

        # 2. Experiment summary counts and uniqueness.
        result = con.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT clickability_test_id),
                SUM(package_count),
                COUNT(*) FILTER (WHERE pooled_ctr IS NULL)
            FROM experiment_summary
        """).fetchone()

        record_check(
            "Experiment summary",
            result[0] == EXPECTED_EXPERIMENTS
            and result[1] == EXPECTED_EXPERIMENTS
            and result[2] == EXPECTED_PACKAGE_ROWS
            and result[3] == 0,
            f"rows={result[0]}, unique IDs={result[1]}, "
            f"source rows={result[2]}, null pooled CTR={result[3]}",
        )

        # 3. Reconcile summary metrics against source rows.
        mismatches = con.execute("""
            WITH recalculated AS (
                SELECT
                    clickability_test_id,
                    SUM(impressions) AS total_impressions,
                    SUM(clicks) AS total_clicks,
                    SUM(clicks)::DOUBLE
                        / NULLIF(SUM(impressions), 0) AS pooled_ctr
                FROM packages
                GROUP BY clickability_test_id
            )
            SELECT COUNT(*)
            FROM experiment_summary s
            JOIN recalculated r USING (clickability_test_id)
            WHERE s.total_impressions <> r.total_impressions
               OR s.total_clicks <> r.total_clicks
               OR ABS(s.pooled_ctr - r.pooled_ctr) > 1e-12
        """).fetchone()[0]

        record_check(
            "Experiment metrics reconcile",
            mismatches == 0,
            f"mismatched experiments={mismatches}",
        )

        # 4. Comparison-candidate counts and keys.
        result = con.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT clickability_test_id),
                COUNT(*) FILTER (WHERE comparison_category IS NULL),
                SUM(package_count)
            FROM comparison_candidates
        """).fetchone()

        record_check(
            "Comparison-candidate dataset",
            result[0] == EXPECTED_EXPERIMENTS
            and result[1] == EXPECTED_EXPERIMENTS
            and result[2] == 0
            and result[3] == EXPECTED_PACKAGE_ROWS,
            f"rows={result[0]}, unique IDs={result[1]}, "
            f"missing categories={result[2]}, source rows={result[3]}",
        )

        # 5. Impression balance: one record per experiment.
        result = con.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT experiment_id),
                COUNT(*) FILTER (WHERE experiment_id IS NULL)
            FROM impression_balance
        """).fetchone()

        record_check(
            "Impression-balance dataset",
            result[0] == EXPECTED_EXPERIMENTS
            and result[1] == EXPECTED_EXPERIMENTS
            and result[2] == 0,
            f"rows={result[0]}, unique IDs={result[1]}, "
            f"null experiment IDs={result[2]}",
        )

        # 6. Comparisons: preserve all source rows and flag zero-click cases.
        result = con.execute("""
            SELECT
                COUNT(*),
                COUNT(DISTINCT row_id),
                COUNT(DISTINCT experiment_id),
                COUNT(*) FILTER (WHERE zero_click_experiment IS NULL),
                COUNT(*) FILTER (WHERE zero_click_experiment)
            FROM within_experiment_comparisons
        """).fetchone()

        record_check(
            "Within-experiment comparisons",
            result[0] == EXPECTED_PACKAGE_ROWS
            and result[1] == EXPECTED_PACKAGE_ROWS
            and result[2] == EXPECTED_EXPERIMENTS
            and result[3] == 0,
            f"rows={result[0]}, unique source row IDs={result[1]}, "
            f"experiments={result[2]}, null zero-click flags={result[3]}, "
            f"zero-click rows={result[4]}",
        )

        # 7. Editorial metadata IDs must match package source-row IDs.
        result = con.execute("""
            WITH package_ids AS (
                SELECT row_id FROM packages
            ),
            metadata_ids AS (
                SELECT row_id FROM editorial_metadata
            )
            SELECT
                (SELECT COUNT(*) FROM metadata_ids),
                (SELECT COUNT(DISTINCT row_id) FROM metadata_ids),
                (
                    SELECT COUNT(*)
                    FROM package_ids p
                    ANTI JOIN metadata_ids m USING (row_id)
                ),
                (
                    SELECT COUNT(*)
                    FROM metadata_ids m
                    ANTI JOIN package_ids p USING (row_id)
                )
        """).fetchone()

        record_check(
            "Editorial metadata row IDs",
            result[0] == EXPECTED_PACKAGE_ROWS
            and result[1] == EXPECTED_PACKAGE_ROWS
            and result[2] == 0
            and result[3] == 0,
            f"metadata rows={result[0]}, unique IDs={result[1]}, "
            f"package IDs missing from metadata={result[2]}, "
            f"metadata IDs missing from packages={result[3]}",
        )

        # Display validation results.
        print("\nCROSS-DATASET VALIDATION")
        print("=" * 80)

        for check in checks:
            print(f"[{check['status']}] {check['check']}")
            print(f"    {check['details']}")

        failures = [
            check for check in checks
            if check["status"] == "FAIL"
        ]

        print("\nSUMMARY")
        print("=" * 80)
        print(f"Checks passed: {len(checks) - len(failures)}/{len(checks)}")
        print(f"Checks failed: {len(failures)}/{len(checks)}")

        if failures:
            raise RuntimeError(
                "Validation failed. Review the checks above."
            )

        print("\nSUCCESS: All analytical datasets passed validation.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
