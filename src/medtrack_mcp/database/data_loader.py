from pathlib import Path
import pandas as pd
from sqlalchemy import text

from medtrack_mcp.database.connection import engine
from medtrack_mcp.database.schema_mapping import TABLE_MAPPINGS


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_ROOT / "data" / "source" / "synthea"


def clean_zip(value):
    if pd.isna(value):
        return None

    value = str(value)

    if value.endswith(".0"):
        value = value[:-2]

    return value


def load_table(table_name):
    mapping = TABLE_MAPPINGS[table_name]

    file_path = SOURCE_DIR / mapping["source_file"]

    print(f"\nLoading {table_name}...")
    print(f"Reading: {file_path}")

    df = pd.read_csv(file_path)

    source_row_count = len(df)

    print(f"Source rows: {source_row_count}")

    df = df.rename(columns=mapping["column_mapping"])

    target_columns = list(mapping["column_mapping"].values())

    df = df[target_columns]

    if "zip" in df.columns:
        df["zip"] = df["zip"].apply(clean_zip)

    for column in mapping["date_columns"]:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        ).dt.date

    df = df.where(pd.notnull(df), None)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

    print(f"Loaded {source_row_count} rows into {table_name}")

    return source_row_count


def get_database_row_count(table_name):
    query = text(f"SELECT COUNT(*) FROM {table_name}")

    with engine.connect() as connection:
        result = connection.execute(query)
        return result.scalar()


def validate_table(table_name, source_row_count):
    database_row_count = get_database_row_count(table_name)

    print(f"\nValidation: {table_name}")
    print(f"CSV rows: {source_row_count}")
    print(f"Database rows: {database_row_count}")

    if source_row_count == database_row_count:
        print("Validation successful.")
    else:
        print("### ERROR ###: Row count mismatch.")


if __name__ == "__main__":
    tables_to_load = [
        "patients",
        "organizations",
        "payers",
        "providers",
        "encounters",
        "conditions",
        "allergies",
        "observations",
        "medications",
        "procedures",
        "careplans",
        "devices",
        "imaging_studies",
        "immunizations",
        "payer_transitions"
    ]


    for table_name in tables_to_load:
        source_row_count = load_table(table_name)
        validate_table(table_name, source_row_count)