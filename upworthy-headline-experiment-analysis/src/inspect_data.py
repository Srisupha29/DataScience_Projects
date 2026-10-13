from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"

csv_files = list(RAW_DIR.glob("*exploratory*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No exploratory CSV found in {RAW_DIR}"
    )

if len(csv_files) > 1:
    raise RuntimeError(
        f"Expected one exploratory CSV, found: {csv_files}"
    )

csv_path = csv_files[0]
con = duckdb.connect()

print("=" * 70)
print("UPWORTHY DATASET INSPECTION")
print("=" * 70)
print(f"\nFile: {csv_path.name}")
print(f"Size: {csv_path.stat().st_size / (1024 * 1024):.2f} MB")

csv_path_sql = str(csv_path).replace("'", "''")

con.execute(
    f"CREATE VIEW upworthy AS "
    f"SELECT * FROM read_csv_auto('{csv_path_sql}')"
)

# Row and column counts
row_count = con.execute(
    "SELECT COUNT(*) FROM upworthy"
).fetchone()[0]

columns = con.execute(
    "DESCRIBE SELECT * FROM upworthy"
).fetchall()

print(f"\nRows: {row_count:,}")
print(f"Columns: {len(columns)}")

print("\n--- COLUMN NAMES AND TYPES ---")
for column_name, column_type, *_ in columns:
    print(f"{column_name}: {column_type}")

print("\n--- FIRST 5 ROWS ---")
print(con.execute("SELECT * FROM upworthy LIMIT 5").df().to_string(index=False))

print("\n--- MISSING VALUES ---")
column_names = [column[0] for column in columns]

for column_name in column_names:
    safe_name = '"' + column_name.replace('"', '""') + '"'
    missing_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM upworthy
        WHERE {safe_name} IS NULL
        """
    ).fetchone()[0]

    if missing_count > 0:
        percentage = missing_count / row_count * 100
        print(
            f"{column_name}: {missing_count:,} "
            f"({percentage:.2f}%)"
        )

print("\n--- POTENTIAL EXPERIMENT IDENTIFIERS ---")
for column_name in column_names:
    if any(
        term in column_name.lower()
        for term in ["test_id", "experiment_id", "package_id"]
    ):
        safe_name = '"' + column_name.replace('"', '""') + '"'
        distinct_count = con.execute(
            f"SELECT COUNT(DISTINCT {safe_name}) FROM upworthy"
        ).fetchone()[0]

        print(f"{column_name}: {distinct_count:,} distinct values")

print("\nInspection complete. No source data was modified.")