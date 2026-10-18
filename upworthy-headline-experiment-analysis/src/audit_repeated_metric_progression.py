from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "data/processed/headline_cohort.parquet"

con = duckdb.connect()

query = f"""
WITH repeated AS (
    SELECT
        clickability_test_id,
        package_id,
        COUNT(*) AS row_count,
        COUNT(DISTINCT created_at) AS created_timestamps,
        COUNT(DISTINCT updated_at) AS updated_timestamps,
        MIN(created_at) AS first_created,
        MAX(created_at) AS last_created,
        MIN(impressions) AS min_impressions,
        MAX(impressions) AS max_impressions,
        MIN(clicks) AS min_clicks,
        MAX(clicks) AS max_clicks,
        COUNT(DISTINCT impressions) AS impression_values,
        COUNT(DISTINCT clicks) AS click_values
    FROM read_parquet('{COHORT}')
    GROUP BY clickability_test_id, package_id
    HAVING COUNT(*) > 1
)
SELECT
    COUNT(*) AS repeated_identities,
    COUNT(*) FILTER (
        WHERE min_impressions >= 0 AND max_impressions >= min_impressions
    ) AS identities_with_nonnegative_impressions,
    COUNT(*) FILTER (
        WHERE min_clicks >= 0 AND max_clicks >= min_clicks
    ) AS identities_with_nonnegative_clicks,
    COUNT(*) FILTER (
        WHERE created_timestamps > 1
    ) AS identities_with_multiple_created_timestamps,
    COUNT(*) FILTER (
        WHERE updated_timestamps > 1
    ) AS identities_with_multiple_updated_timestamps,
    COUNT(*) FILTER (
        WHERE impression_values > 1
    ) AS identities_with_changing_impressions,
    COUNT(*) FILTER (
        WHERE click_values > 1
    ) AS identities_with_changing_clicks
FROM repeated
"""

print("--- Repeated identity metric summary ---")
print(con.execute(query).fetchdf().to_string(index=False))

print("\n--- Example repeated identities, ordered by time ---")
print(con.execute(f"""
    SELECT
        clickability_test_id,
        package_id,
        created_at,
        updated_at,
        impressions,
        clicks
    FROM read_parquet('{COHORT}')
    WHERE package_id IN (
        SELECT package_id
        FROM read_parquet('{COHORT}')
        GROUP BY package_id
        HAVING COUNT(*) > 1
    )
    ORDER BY package_id, created_at
    LIMIT 20
""").fetchdf().to_string(index=False))

con.close()
