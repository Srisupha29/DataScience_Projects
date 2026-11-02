import duckdb
from utils.utils import (
    EXPECTED_EXPERIMENTS,
    EXPECTED_PACKAGE_ROWS,
    PROCESSED_DIR,
)

FILE = PROCESSED_DIR / "comparison_candidates.parquet"
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
    """, [str(FILE)]).fetchone()

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

    expected_values = [
        EXPECTED_EXPERIMENTS,
        EXPECTED_EXPERIMENTS,
        2301,
        EXPECTED_EXPERIMENTS - 2301,
        0,
        0,
        0,
        0,
        EXPECTED_PACKAGE_ROWS,
    ]

    failures = [
        f"{label}: got {actual}, expected {wanted}"
        for label, actual, wanted in zip(labels, result, expected_values)
        if actual != wanted
    ]

    if failures:
        raise ValueError(
            "VALIDATION FAILED:\n" + "\n".join(failures)
        )

    print("\nSUCCESS: Eligibility flag passed all checks.")

finally:
    con.close()