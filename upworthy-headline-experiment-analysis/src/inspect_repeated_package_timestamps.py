from pathlib import Path
import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
PACKAGES_FILE = PROJECT_DIR / "data" / "processed" / "packages.parquet"


def main():
    con = duckdb.connect(database=":memory:")

    try:
        con.read_parquet(str(PACKAGES_FILE)).create_view("packages")

        results = con.execute("""
            SELECT
                COUNT(*) AS repeated_identities,
                COUNT(*) FILTER (
                    WHERE distinct_timestamps = 1
                ) AS one_timestamp,
                COUNT(*) FILTER (
                    WHERE distinct_timestamps > 1
                ) AS multiple_timestamps,
                COUNT(*) FILTER (
                    WHERE missing_timestamps > 0
                ) AS identities_with_missing_timestamps
            FROM (
                SELECT
                    package_id,
                    COUNT(DISTINCT created_at) AS distinct_timestamps,
                    COUNT(*) FILTER (
                        WHERE created_at IS NULL
                    ) AS missing_timestamps
                FROM packages
                GROUP BY package_id
                HAVING COUNT(*) > 1
            ) AS repeated
        """).df()

        print("\nREPEATED PACKAGE TIMESTAMP CHECK")
        print("=" * 60)
        print(results.to_string(index=False))

        examples = con.execute("""
            SELECT
                package_id,
                created_at,
                impressions,
                clicks,
                row_id
            FROM packages
            WHERE package_id IN (
                SELECT package_id
                FROM packages
                GROUP BY package_id
                HAVING COUNT(*) > 1
            )
            ORDER BY package_id, created_at
            LIMIT 20
        """).df()

        print("\nEXAMPLE SOURCE ROWS")
        print("=" * 60)
        print(examples.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    main()