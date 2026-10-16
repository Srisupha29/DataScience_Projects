from pathlib import Path
import duckdb

# 1. Locate the project and source data.
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "upworthy-archive-exploratory-packages-03.12.2020.csv"
)
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "packages.parquet"


def main():
    # 2. Check that the source file exists.
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Source CSV not found: {RAW_FILE}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 3. Connect to an in-memory DuckDB database.
    con = duckdb.connect(database=":memory:")

    try:
        # 4. Read the CSV without modifying the original file.
        packages = con.read_csv(
            str(RAW_FILE),
            header=True,
            auto_detect=True,
        )
        packages.create_view("source_packages")

        # 5. Inspect the schema.
        print("\nDATASET SCHEMA")
        print("=" * 60)
        print(con.execute("DESCRIBE source_packages").df().to_string(index=False))

        # 6. Validate the basic dataset structure.
        summary = con.execute("""
            SELECT
                COUNT(*) AS total_packages,
                COUNT(DISTINCT clickability_test_id) AS total_experiments,
                COUNT(*) FILTER (
                    WHERE clickability_test_id IS NULL
                ) AS missing_experiment_ids,
                COUNT(*) FILTER (
                    WHERE impressions IS NULL
                ) AS missing_impressions,
                COUNT(*) FILTER (
                    WHERE clicks IS NULL
                ) AS missing_clicks,
                COUNT(*) FILTER (
                    WHERE impressions <= 0
                ) AS nonpositive_impressions,
                COUNT(*) FILTER (
                    WHERE clicks < 0 OR clicks > impressions
                ) AS invalid_click_counts
            FROM source_packages
        """).df()

        print("\nVALIDATION SUMMARY")
        print("=" * 60)
        print(summary.to_string(index=False))

        # 7. Export a reproducible analytical copy in Parquet format.
        packages.write_parquet(str(OUTPUT_FILE), compression="zstd")

        print("\nOUTPUT")
        print("=" * 60)
        print(f"Parquet file: {OUTPUT_FILE}")
        print(f"File size: {OUTPUT_FILE.stat().st_size / (1024 ** 2):.2f} MB")

        # 8. Confirm the exported file can be read.
        exported_rows = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [str(OUTPUT_FILE)],
        ).fetchone()[0]

        print(f"Rows exported: {exported_rows:,}")

        if exported_rows != summary.iloc[0]["total_packages"]:
            raise ValueError("Exported row count does not match source row count.")

        print("\nSUCCESS: Exported row count matches the source.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
