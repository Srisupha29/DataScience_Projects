
from utils import (
    PACKAGES_FILE,
    EXPERIMENT_SUMMARY_FILE,
    COMPARISON_CANDIDATES_FILE,
    get_connection,
    load_parquet_view,
)


def main():
    required_files = [
        PACKAGES_FILE,
        EXPERIMENT_SUMMARY_FILE,
        COMPARISON_CANDIDATES_FILE,
    ]

    for file_path in required_files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )

    con = get_connection()

    try:
        # Register all three datasets.
        load_parquet_view(con, "packages", PACKAGES_FILE)
        load_parquet_view(
            con,
            "experiment_summary",
            EXPERIMENT_SUMMARY_FILE,
        )
        load_parquet_view(
            con,
            "comparison_candidates",
            COMPARISON_CANDIDATES_FILE,
        )

        checks = []

        def record_check(name, passed, details):
            checks.append({
                "check": name,
                "status": "PASS" if passed else "FAIL",
                "details": str(details),
            })

        # Check 1: package-level dataset counts.
        package_result = con.execute("""
            SELECT
                COUNT(*) AS row_count,
                COUNT(DISTINCT clickability_test_id)
                    AS experiment_count,
                COUNT(*) FILTER (WHERE ctr IS NULL)
                    AS null_ctr_count,
                COUNT(*) FILTER (
                    WHERE ABS(
                        ctr - clicks::DOUBLE
                        / NULLIF(impressions, 0)
                    ) > 1e-12
                ) AS incorrect_ctr_count
            FROM packages
        """).fetchone()

        record_check(
            "Package dataset",
            package_result[0] == 22666
            and package_result[1] == 4873
            and package_result[2] == 0
            and package_result[3] == 0,
            f"rows={package_result[0]}, "
            f"experiments={package_result[1]}, "
            f"null CTR={package_result[2]}, "
            f"incorrect CTR={package_result[3]}",
        )

        # Check 2: experiment summary uniqueness and package totals.
        summary_result = con.execute("""
            SELECT
                COUNT(*) AS row_count,
                COUNT(DISTINCT clickability_test_id) AS unique_ids,
                SUM(package_count) AS package_total,
                COUNT(*) FILTER (
                    WHERE pooled_ctr IS NULL
                ) AS null_pooled_ctr
            FROM experiment_summary
        """).fetchone()

        record_check(
            "Experiment summary",
            summary_result[0] == 4873
            and summary_result[1] == 4873
            and summary_result[2] == 22666
            and summary_result[3] == 0,
            f"rows={summary_result[0]}, "
            f"unique IDs={summary_result[1]}, "
            f"package total={summary_result[2]}, "
            f"null pooled CTR={summary_result[3]}",
        )

        # Check 3: summary metrics agree with the package dataset.
        metric_mismatches = con.execute("""
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
            FROM experiment_summary AS s
            JOIN recalculated AS r USING (clickability_test_id)
            WHERE s.total_impressions <> r.total_impressions
               OR s.total_clicks <> r.total_clicks
               OR ABS(s.pooled_ctr - r.pooled_ctr) > 1e-12
        """).fetchone()[0]

        record_check(
            "Experiment metrics reconcile",
            metric_mismatches == 0,
            "experiments with mismatched aggregate metrics="
            f"{metric_mismatches}",
        )

        # Check 4: comparison-candidate keys and row totals.
        candidate_result = con.execute("""
            SELECT
                COUNT(*) AS row_count,
                COUNT(DISTINCT clickability_test_id) AS unique_ids,
                COUNT(*) FILTER (
                    WHERE comparison_category IS NULL
                ) AS missing_categories
            FROM comparison_candidates
        """).fetchone()

        record_check(
            "Comparison-candidate dataset",
            candidate_result[0] == 4873
            and candidate_result[1] == 4873
            and candidate_result[2] == 0,
            f"rows={candidate_result[0]}, "
            f"unique IDs={candidate_result[1]}, "
            f"missing categories={candidate_result[2]}",
        )

        # Check 5: category totals match the expected Phase 1 findings.
        category_counts = dict(con.execute("""
            SELECT comparison_category, COUNT(*)
            FROM comparison_candidates
            GROUP BY comparison_category
        """).fetchall())

        expected_counts = {
            "Headline variation candidate": 2304,
            "Image variation candidate": 1426,
            "No recorded headline or image variation": 838,
            "Mixed headline and image variation": 300,
            "No recorded image ID": 5,
        }

        record_check(
            "Classification counts",
            category_counts == expected_counts,
            f"observed={category_counts}",
        )

        # Display the results.
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
                "Validation failed. Review the checks above before proceeding."
            )

        print("\nSUCCESS: All analytical datasets passed validation.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
