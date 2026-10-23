from utils.utils import (
    RAW_FILE,
    PROCESSED_DIR,
    PACKAGES_FILE,
    EDITORIAL_FILE,
    EXPECTED_PACKAGE_ROWS,
    EXPECTED_EXPERIMENTS,
    normalize_headline_sql,
    get_connection,
    load_raw_view,
)

EDITORIAL_COLUMNS = ["winner", "first_place", "significance"]


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Source CSV not found: {RAW_FILE}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    con = get_connection()

    try:
        load_raw_view(con)

        source_summary = con.execute("""
            SELECT
                COUNT(*) AS total_rows,
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
                ) AS invalid_click_counts,
                COUNT(*) FILTER (
                    WHERE column00 IS NULL
                ) AS missing_row_ids
            FROM source_packages
        """).df()

        print("\nSOURCE VALIDATION")
        print("=" * 60)
        print(source_summary.to_string(index=False))

        checks = source_summary.iloc[0]

        validation_rules = {
            "total_rows": (
                lambda value: value == EXPECTED_PACKAGE_ROWS,
                f"Expected {EXPECTED_PACKAGE_ROWS:,} source rows.",
            ),
            "total_experiments": (
                lambda value: value == EXPECTED_EXPERIMENTS,
                f"Expected {EXPECTED_EXPERIMENTS:,} experiments.",
            ),
            "missing_experiment_ids": (
                lambda value: value == 0,
                "Missing experiment IDs were found.",
            ),
            "missing_impressions": (
                lambda value: value == 0,
                "Missing impression counts were found.",
            ),
            "missing_clicks": (
                lambda value: value == 0,
                "Missing click counts were found.",
            ),
            "nonpositive_impressions": (
                lambda value: value == 0,
                "Rows with nonpositive impressions were found.",
            ),
            "invalid_click_counts": (
                lambda value: value == 0,
                "Rows with invalid click counts were found.",
            ),
            "missing_row_ids": (
                lambda value: value == 0,
                "Missing source row IDs were found.",
            ),
        }

        validation_errors = [
            message
            for column, (condition, message) in validation_rules.items()
            if not condition(checks[column])
        ]

        if validation_errors:
            raise ValueError(
                "Source validation failed:\n- "
                + "\n- ".join(validation_errors)
            )

        normalized_headline = normalize_headline_sql(
            "headline"
        )

        con.execute(f"""
            CREATE VIEW analytical_packages AS
            SELECT
                column00 AS row_id,
                sha256(
                    to_json(
                        struct_pack(
                            experiment_id := clickability_test_id,
                            headline := {normalized_headline},
                            image_id := coalesce(
                                eyecatcher_id,
                                '<MISSING_IMAGE_ID>'
                            )
                        )
                    )
                ) AS package_id,
                * EXCLUDE (
                    column00,
                    winner,
                    first_place,
                    significance
                ),
                {normalized_headline} AS normalized_headline,
                clicks::DOUBLE / NULLIF(impressions, 0) AS ctr
            FROM source_packages
        """)

        con.execute("""
            CREATE VIEW editorial_metadata AS
            SELECT
                column00 AS row_id,
                winner,
                first_place,
                significance
            FROM source_packages
        """)

        # Diagnose repeated package IDs before deciding whether
        # multiple rows represent disjoint time slices or snapshots.
        repeated_packages = con.execute("""
            SELECT
                clickability_test_id AS experiment_id,
                package_id,
                COUNT(*) AS source_row_count,
                COUNT(DISTINCT created_at) AS distinct_created_at,
                COUNT(DISTINCT updated_at) AS distinct_updated_at,
                MIN(created_at) AS first_created_at,
                MAX(created_at) AS last_created_at,
                MIN(updated_at) AS first_updated_at,
                MAX(updated_at) AS last_updated_at,
                SUM(impressions) AS summed_impressions,
                SUM(clicks) AS summed_clicks,
                MIN(impressions) AS min_row_impressions,
                MAX(impressions) AS max_row_impressions
            FROM analytical_packages
            GROUP BY
                clickability_test_id,
                package_id
            HAVING COUNT(*) > 1
            ORDER BY source_row_count DESC, experiment_id
        """).df()

        print("\nREPEATED PACKAGE DIAGNOSTICS")
        print("=" * 60)
        print(
            "Repeated package groups: "
            f"{len(repeated_packages):,}"
        )

        if not repeated_packages.empty:
            print(
                "Source rows belonging to repeated groups: "
                f"{repeated_packages['source_row_count'].sum():,}"
            )
            print("\nLargest repeated groups:")
            print(
                repeated_packages.head(10).to_string(index=False)
            )
            print(
                "\nInterpretation: timestamp differences alone do not "
                "establish whether counts are additive time slices "
                "or repeated snapshots. No aggregation is performed "
                "by this script."
            )

        identifier_checks = con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT row_id) AS distinct_row_ids,
                COUNT(*) FILTER (
                    WHERE row_id IS NULL
                ) AS missing_row_ids,
                COUNT(*) FILTER (
                    WHERE package_id IS NULL
                ) AS missing_package_ids,
                COUNT(DISTINCT package_id) AS distinct_package_ids
            FROM analytical_packages
        """).df()

        print("\nIDENTIFIER VALIDATION")
        print("=" * 60)
        print(identifier_checks.to_string(index=False))

        ids = identifier_checks.iloc[0]

        if ids["total_rows"] != ids["distinct_row_ids"]:
            raise ValueError("Source row IDs are not unique.")

        if ids["missing_row_ids"] != 0:
            raise ValueError("Missing row IDs were found.")

        if ids["missing_package_ids"] != 0:
            raise ValueError("Missing package IDs were found.")

        if ids["total_rows"] != checks["total_rows"]:
            raise ValueError(
                "Analytical row count differs from source row count."
            )

        con.table("analytical_packages").write_parquet(
            str(PACKAGES_FILE),
            compression="zstd",
        )

        con.table("editorial_metadata").write_parquet(
            str(EDITORIAL_FILE),
            compression="zstd",
        )

        exported_packages = con.execute(
            "SELECT * FROM read_parquet(?)",
            [str(PACKAGES_FILE)],
        ).df()

        exported_metadata = con.execute(
            "SELECT * FROM read_parquet(?)",
            [str(EDITORIAL_FILE)],
        ).df()

        package_columns = set(exported_packages.columns)
        metadata_columns = set(exported_metadata.columns)

        forbidden_columns = set(EDITORIAL_COLUMNS) & package_columns

        if forbidden_columns:
            raise ValueError(
                "Editorial metadata leaked into packages.parquet: "
                f"{sorted(forbidden_columns)}"
            )

        if not set(EDITORIAL_COLUMNS).issubset(metadata_columns):
            raise ValueError(
                "Editorial metadata file is missing expected columns."
            )

        if len(exported_packages) != len(exported_metadata):
            raise ValueError(
                "Package data and editorial metadata row counts do not match."
            )

        if exported_metadata["row_id"].duplicated().any():
            raise ValueError("Editorial metadata row IDs are not unique.")

        if set(exported_packages["row_id"]) != set(
            exported_metadata["row_id"]
        ):
            raise ValueError(
                "Package and editorial metadata row IDs do not match."
            )

        print("\nEXPORT VALIDATION")
        print("=" * 60)
        print(f"Packages file: {PACKAGES_FILE}")
        print(f"Packages rows: {len(exported_packages):,}")
        print(f"Packages columns: {len(exported_packages.columns)}")
        print(f"Editorial metadata file: {EDITORIAL_FILE}")
        print(f"Editorial metadata rows: {len(exported_metadata):,}")
        print(
            "Editorial metadata columns: "
            f"{len(exported_metadata.columns)}"
        )
        print(
            "Editorial columns in packages.parquet: "
            f"{sorted(forbidden_columns)}"
        )
        print("All checks passed.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
