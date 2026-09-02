from pathlib import Path
import pandas as pd
from medtrack_mcp.database.schema_mapping import TABLE_MAPPINGS


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_ROOT / "data" / "source" / "synthea"

TABLES_TO_INSPECT = [
    "patients",
    "organizations",
    "payers",
]


def inspect_table(table_name):
    mapping = TABLE_MAPPINGS[table_name]

    file_path = SOURCE_DIR / mapping["source_file"]

    print("\n" + "=" * 60)
    print(f"TABLE: {table_name}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn Mapping:")
    for source_column, target_column in mapping["column_mapping"].items():
        status = "OK" if source_column in df.columns else "MISSING"
        print(f"{source_column} -> {target_column} [{status}]")

    print("\nPrimary Key Check:")

    primary_key = mapping["primary_key"]

    if primary_key != "generated":
        source_primary_key = None

        for source_column, target_column in mapping["column_mapping"].items():
            if target_column == primary_key:
                source_primary_key = source_column
                break

        if source_primary_key:
            print(f"Primary Key: {source_primary_key}")
            print(f"Null values: {df[source_primary_key].isnull().sum()}")
            print(f"Duplicate values: {df[source_primary_key].duplicated().sum()}")

    print("\nNull Values:")

    null_counts = df.isnull().sum()
    null_counts = null_counts[null_counts > 0]

    if len(null_counts) == 0:
        print("No null values")
    else:
        print(null_counts.to_string())

    print("\nSample Data:")
    print(df.head(3).to_string())

    print("\nData Types:")
    print(df.dtypes.to_string())


def inspect_all_tables():
    for table_name in TABLES_TO_INSPECT:
        inspect_table(table_name)


if __name__ == "__main__":
    inspect_all_tables()