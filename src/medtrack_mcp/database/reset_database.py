from sqlalchemy import text
from medtrack_mcp.database.connection import engine


TABLES = [
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


def reset_database():
    print("Resetting MedTrack database...")

    table_names = ", ".join(TABLES)

    query = text(
        f"TRUNCATE TABLE {table_names} "
        "RESTART IDENTITY CASCADE"
    )

    with engine.begin() as connection:
        connection.execute(query)

    print("Database reset successfully.")


if __name__ == "__main__":
    reset_database()