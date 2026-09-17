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


FOREIGN_KEY_CHECKS = [
    {
        "name": "providers.organization_id -> organizations.id",
        "child_table": "providers",
        "child_column": "organization_id",
        "parent_table": "organizations",
        "parent_column": "id"
    },
    {
        "name": "encounters.patient_id -> patients.id",
        "child_table": "encounters",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "encounters.organization_id -> organizations.id",
        "child_table": "encounters",
        "child_column": "organization_id",
        "parent_table": "organizations",
        "parent_column": "id"
    },
    {
        "name": "encounters.provider_id -> providers.id",
        "child_table": "encounters",
        "child_column": "provider_id",
        "parent_table": "providers",
        "parent_column": "id"
    },
    {
        "name": "encounters.payer_id -> payers.id",
        "child_table": "encounters",
        "child_column": "payer_id",
        "parent_table": "payers",
        "parent_column": "id"
    },
    {
        "name": "conditions.patient_id -> patients.id",
        "child_table": "conditions",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "conditions.encounter_id -> encounters.id",
        "child_table": "conditions",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "allergies.patient_id -> patients.id",
        "child_table": "allergies",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "allergies.encounter_id -> encounters.id",
        "child_table": "allergies",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "observations.patient_id -> patients.id",
        "child_table": "observations",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "observations.encounter_id -> encounters.id",
        "child_table": "observations",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "medications.patient_id -> patients.id",
        "child_table": "medications",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "medications.payer_id -> payers.id",
        "child_table": "medications",
        "child_column": "payer_id",
        "parent_table": "payers",
        "parent_column": "id"
    },
    {
        "name": "medications.encounter_id -> encounters.id",
        "child_table": "medications",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "procedures.patient_id -> patients.id",
        "child_table": "procedures",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "procedures.encounter_id -> encounters.id",
        "child_table": "procedures",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "careplans.patient_id -> patients.id",
        "child_table": "careplans",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "careplans.encounter_id -> encounters.id",
        "child_table": "careplans",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "devices.patient_id -> patients.id",
        "child_table": "devices",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "devices.encounter_id -> encounters.id",
        "child_table": "devices",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "imaging_studies.patient_id -> patients.id",
        "child_table": "imaging_studies",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "imaging_studies.encounter_id -> encounters.id",
        "child_table": "imaging_studies",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "immunizations.patient_id -> patients.id",
        "child_table": "immunizations",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "immunizations.encounter_id -> encounters.id",
        "child_table": "immunizations",
        "child_column": "encounter_id",
        "parent_table": "encounters",
        "parent_column": "id"
    },
    {
        "name": "payer_transitions.patient_id -> patients.id",
        "child_table": "payer_transitions",
        "child_column": "patient_id",
        "parent_table": "patients",
        "parent_column": "id"
    },
    {
        "name": "payer_transitions.payer_id -> payers.id",
        "child_table": "payer_transitions",
        "child_column": "payer_id",
        "parent_table": "payers",
        "parent_column": "id"
    }
]


def validate_row_counts():
    print("\n" + "=" * 60)
    print("ROW COUNT VALIDATION")
    print("=" * 60)

    with engine.connect() as connection:
        for table in TABLES:
            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )

            count = result.scalar()

            print(f"{table}: {count}")


def validate_foreign_keys():
    print("\n" + "=" * 60)
    print("FOREIGN KEY VALIDATION")
    print("=" * 60)

    all_valid = True

    with engine.connect() as connection:

        for check in FOREIGN_KEY_CHECKS:

            query = text(f"""
                SELECT COUNT(*)
                FROM {check["child_table"]} child
                LEFT JOIN {check["parent_table"]} parent
                ON child.{check["child_column"]} =
                   parent.{check["parent_column"]}
                WHERE child.{check["child_column"]} IS NOT NULL
                AND parent.{check["parent_column"]} IS NULL
            """)

            result = connection.execute(query)
            invalid_count = result.scalar()

            if invalid_count == 0:
                print(f"PASS: {check["name"]}")
            else:
                print(
                    f"FAIL: {check["name"]} "
                    f"({invalid_count} invalid references)"
                )

                all_valid = False

    return all_valid


def run_validation():

    print("\nMEDTRACK DATABASE VALIDATION")

    validate_row_counts()

    foreign_keys_valid = validate_foreign_keys()

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if foreign_keys_valid:
        print("DATABASE BASELINE VALIDATED SUCCESSFULLY")
    else:
        print("DATABASE VALIDATION FAILED")


if __name__ == "__main__":
    run_validation()