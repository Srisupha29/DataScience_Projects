from utils.utils import RAW_FILE, get_connection, load_raw_view

EXPERIMENT_IDS = [
    "53480581be4154443a000008",
    "52930ef6d40ad9e426003b53",
]


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Source CSV not found: {RAW_FILE}")
    con = get_connection()
    try:
        load_raw_view(con, "upworthy")
        print("DATASET OVERVIEW")
        print("=" * 70)
        print(f"File: {RAW_FILE.name}")
        print(f"Rows: {con.execute('SELECT COUNT(*) FROM upworthy').fetchone()[0]:,}")
        print(con.execute("DESCRIBE SELECT * FROM upworthy").df().to_string(index=False))
        print("\nMISSING VALUES BY COLUMN")
        columns = con.execute("DESCRIBE SELECT * FROM upworthy").fetchall()
        row_count = con.execute("SELECT COUNT(*) FROM upworthy").fetchone()[0]
        for column in columns:
            name = column[0]
            safe_name = '"' + name.replace('"', '""') + '"'
            count = con.execute(
                f"SELECT COUNT(*) FROM upworthy WHERE {safe_name} IS NULL"
            ).fetchone()[0]
            if count:
                print(f"{name}: {count:,} ({count / row_count * 100:.2f}%)")

        for experiment_id in EXPERIMENT_IDS:
            print(f"\nSELECTED EXPERIMENT: {experiment_id}")
            print(con.execute("""
                SELECT column00, headline, slug, eyecatcher_id, impressions, clicks,
                       ROUND(100.0 * clicks / NULLIF(impressions, 0), 4) AS ctr_pct,
                       significance, first_place, winner
                FROM upworthy
                WHERE clickability_test_id = ?
                ORDER BY slug
            """, [experiment_id]).df().to_string(index=False))
            print("\nVARIATION SUMMARY")
            print(con.execute("""
                SELECT COUNT(*) AS row_count,
                       COUNT(DISTINCT headline) AS distinct_headlines,
                       COUNT(DISTINCT slug) AS distinct_slugs,
                       COUNT(DISTINCT eyecatcher_id) AS distinct_image_ids,
                       COUNT(DISTINCT impressions) AS distinct_impression_counts,
                       COUNT(DISTINCT clicks) AS distinct_click_counts
                FROM upworthy
                WHERE clickability_test_id = ?
            """, [experiment_id]).df().to_string(index=False))
        print("\nInspection complete. Source CSV was not modified.")
    finally:
        con.close()


if __name__ == "__main__":
    main()
