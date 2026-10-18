
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "data/processed/headline_cohort.parquet"

con = duckdb.connect()

print("--- Repeated identity field differences ---")
print(con.execute(f"""
    WITH repeated AS (
        SELECT package_id
        FROM read_parquet('{COHORT}')
        GROUP BY clickability_test_id, package_id
        HAVING COUNT(*) > 1
    ),
    details AS (
        SELECT
            p.clickability_test_id,
            p.package_id,
            COUNT(*) AS rows,
            COUNT(DISTINCT p.headline) AS raw_headlines,
            COUNT(DISTINCT p.normalized_headline) AS normalized_headlines,
            COUNT(DISTINCT p.eyecatcher_id) AS image_ids,
            COUNT(DISTINCT p.slug) AS slugs,
            COUNT(DISTINCT p.test_week) AS test_weeks,
            COUNT(DISTINCT p.created_at) AS created_timestamps,
            COUNT(DISTINCT p.impressions) AS impression_values,
            COUNT(DISTINCT p.clicks) AS click_values
        FROM read_parquet('{COHORT}') p
        INNER JOIN repeated r USING (package_id)
        GROUP BY p.clickability_test_id, p.package_id
    )
    SELECT
        COUNT(*) AS repeated_identities,
        COUNT(*) FILTER (WHERE raw_headlines > 1)
            AS identities_with_different_raw_headlines,
        COUNT(*) FILTER (WHERE normalized_headlines > 1)
            AS identities_with_different_normalized_headlines,
        COUNT(*) FILTER (WHERE image_ids > 1)
            AS identities_with_different_image_ids,
        COUNT(*) FILTER (WHERE slugs > 1)
            AS identities_with_different_slugs,
        COUNT(*) FILTER (WHERE test_weeks > 1)
            AS identities_with_different_test_weeks,
        COUNT(*) FILTER (WHERE created_timestamps > 1)
            AS identities_with_multiple_created_timestamps
    FROM details
""").fetchdf().to_string(index=False))

print("\n--- Example repeated records ---")
print(con.execute(f"""
    SELECT
        clickability_test_id,
        row_id,
        package_id,
        created_at,
        headline,
        slug,
        eyecatcher_id,
        test_week,
        impressions,
        clicks
    FROM read_parquet('{COHORT}')
    WHERE (clickability_test_id, package_id) IN (
        SELECT clickability_test_id, package_id
        FROM read_parquet('{COHORT}')
        GROUP BY clickability_test_id, package_id
        HAVING COUNT(*) > 1
    )
    ORDER BY package_id, created_at
    LIMIT 20
""").fetchdf().to_string(index=False))

con.close()
