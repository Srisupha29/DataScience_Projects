from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "data/processed/headline_cohort.parquet"

con = duckdb.connect()

print("\n--- Cohort record audit ---")
print(con.execute(f"""
    SELECT
        COUNT(*) AS source_rows,
        COUNT(DISTINCT clickability_test_id) AS experiments,
        COUNT(DISTINCT package_id) AS distinct_packages,
        COUNT(*) - COUNT(DISTINCT package_id) AS extra_package_rows,
        COUNT(*) FILTER (
            WHERE impressions IS NULL OR clicks IS NULL
        ) AS rows_missing_metrics
    FROM read_parquet('{COHORT}')
""").fetchdf().to_string(index=False))

print("\n--- Repeated package identities ---")
print(con.execute(f"""
    WITH package_audit AS (
        SELECT
            clickability_test_id,
            package_id,
            COUNT(*) AS row_count,
            COUNT(DISTINCT created_at) AS timestamps,
            COUNT(DISTINCT impressions) AS impression_values,
            COUNT(DISTINCT clicks) AS click_values
        FROM read_parquet('{COHORT}')
        GROUP BY clickability_test_id, package_id
    )
    SELECT
        COUNT(*) FILTER (WHERE row_count > 1)
            AS repeated_package_identities,
        SUM(row_count - 1) FILTER (WHERE row_count > 1)
            AS extra_rows_from_repeats,
        COUNT(*) FILTER (
            WHERE row_count > 1
              AND (impression_values > 1 OR click_values > 1)
        ) AS repeated_identities_with_changing_metrics,
        COUNT(*) FILTER (
            WHERE row_count > 1 AND timestamps > 1
        ) AS repeated_identities_with_multiple_timestamps
    FROM package_audit
""").fetchdf().to_string(index=False))

print("\n--- Experiments affected by repeated package rows ---")
print(con.execute(f"""
    SELECT COUNT(*) AS affected_experiments
    FROM (
        SELECT clickability_test_id
        FROM read_parquet('{COHORT}')
        GROUP BY clickability_test_id
        HAVING COUNT(*) > COUNT(DISTINCT package_id)
    ) AS affected
""").fetchdf().to_string(index=False))

con.close()
