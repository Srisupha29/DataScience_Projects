from utils.utils import RAW_FILE, get_connection, load_raw_view


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source CSV not found: {RAW_FILE}"
        )

    con = get_connection()

    try:
        print("=" * 70)
        print("UPWORTHY DATASET INSPECTION")
        print("=" * 70)
        print(f"\nFile: {RAW_FILE.name}")
        print(
            f"Size: {RAW_FILE.stat().st_size / (1024 * 1024):.2f} MB"
        )

        load_raw_view(con, "upworthy")

        # Row and column counts.
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
        print(
            con.execute(
                "SELECT * FROM upworthy LIMIT 5"
            ).df().to_string(index=False)
        )

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
                for term in [
                    "test_id",
                    "experiment_id",
                    "package_id",
                ]
            ):
                safe_name = (
                    '"' + column_name.replace('"', '""') + '"'
                )

                distinct_count = con.execute(
                    f"""
                    SELECT COUNT(DISTINCT {safe_name})
                    FROM upworthy
                    """
                ).fetchone()[0]

                print(
                    f"{column_name}: "
                    f"{distinct_count:,} distinct values"
                )

        print(
            "\nInspection complete. No source data was modified."
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()