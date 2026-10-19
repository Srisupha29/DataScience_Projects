
import duckdb

FILE = "data/processed/comparison_candidates.parquet"
con = duckdb.connect()

try:
    result = con.execute("""
        SELECT
            COUNT(*) AS total_experiments,
            COUNT(DISTINCT clickability_test_id)
                AS unique_experiment_ids,

            COUNT(*) FILTER (
                WHERE primary_headline_structural_eligible IS TRUE
            ) AS eligible_experiments,

            COUNT(*) FILTER (
                WHERE primary_headline_structural_eligible IS FALSE
            ) AS ineligible_experiments,

            COUNT(*) FILTER (
                WHERE primary_headline_structural_eligible IS NULL
            ) AS null_flags,

            COUNT(*) FILTER (
                WHERE primary_headline_structural_eligible IS TRUE
                  AND NOT (
                      distinct_headlines > 1
                      AND distinct_image_ids = 1
                      AND missing_image_id_packages = 0
                  )
            ) AS invalid_true_flags,

            COUNT(*) FILTER (
                WHERE primary_headline_structural_eligible IS FALSE
                  AND distinct_headlines > 1
                  AND distinct_image_ids = 1
                  AND missing_image_id_packages = 0
            ) AS invalid_false_flags,

            COUNT(*) FILTER (
                WHERE primary_headline_structural_eligible IS TRUE
                  AND comparison_category !=
                      'Headline variation candidate'
            ) AS category_mismatches,

            SUM(package_count) AS total_source_rows
        FROM read_parquet(?)
    """, [FILE]).fetchone()

    labels = [
        "Total experiments",
        "Unique experiment IDs",
        "Eligible experiments",
        "Ineligible experiments",
        "Null flags",
        "Invalid TRUE flags",
        "Invalid FALSE flags",
        "Category mismatches",
        "Total source rows",
    ]

    for label, value in zip(labels, result):
        print(f"{label}: {value}")

    expected = {
        "Total experiments": 4873,
        "Unique experiment IDs": 4873,
        "Eligible experiments": 2301,
        "Ineligible experiments": 2572,
        "Null flags": 0,
        "Invalid TRUE flags": 0,
        "Invalid FALSE flags": 0,
        "Category mismatches": 0,
        "Total source rows": 22666,
    }

    failures = [
        f"{label}: got {actual}, expected {wanted}"
        for label, actual, wanted in zip(labels, result, expected.values())
        if actual != wanted
    ]

    if failures:
        raise ValueError(
            "VALIDATION FAILED:\n" + "\n".join(failures)
        )

    print("\nSUCCESS: Eligibility flag passed all checks.")

finally:
    con.close()
