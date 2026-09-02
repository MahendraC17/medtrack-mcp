TABLE_MAPPINGS = {

    "patients": {
        "source_file": "patients.csv",
        "target_table": "patients",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "BIRTHDATE": "birth_date",
            "DEATHDATE": "death_date",
            "SSN": "ssn",
            "DRIVERS": "drivers_license",
            "PASSPORT": "passport",
            "PREFIX": "prefix",
            "FIRST": "first_name",
            "LAST": "last_name",
            "SUFFIX": "suffix",
            "MAIDEN": "maiden_name",
            "MARITAL": "marital_status",
            "RACE": "race",
            "ETHNICITY": "ethnicity",
            "GENDER": "gender",
            "BIRTHPLACE": "birthplace",
            "ADDRESS": "address",
            "CITY": "city",
            "STATE": "state",
            "COUNTY": "county",
            "ZIP": "zip",
            "LAT": "latitude",
            "LON": "longitude",
            "HEALTHCARE_EXPENSES": "healthcare_expenses",
            "HEALTHCARE_COVERAGE": "healthcare_coverage",
        },

        "foreign_keys": {},
        "date_columns": [
            "birth_date",
            "death_date",
        ],
    },


    "organizations": {
        "source_file": "organizations.csv",
        "target_table": "organizations",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "NAME": "name",
            "ADDRESS": "address",
            "CITY": "city",
            "STATE": "state",
            "ZIP": "zip",
            "LAT": "latitude",
            "LON": "longitude",
            "PHONE": "phone",
            "REVENUE": "revenue",
            "UTILIZATION": "utilization",
        },

        "foreign_keys": {},
        "date_columns": [],
    },


    "payers": {
        "source_file": "payers.csv",
        "target_table": "payers",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "NAME": "name",
            "ADDRESS": "address",
            "CITY": "city",
            "STATE_HEADQUARTERED": "state_headquartered",
            "ZIP": "zip",
            "PHONE": "phone",
            "AMOUNT_COVERED": "amount_covered",
            "AMOUNT_UNCOVERED": "amount_uncovered",
            "REVENUE": "revenue",
            "COVERED_ENCOUNTERS": "covered_encounters",
            "UNCOVERED_ENCOUNTERS": "uncovered_encounters",
            "COVERED_MEDICATIONS": "covered_medications",
            "UNCOVERED_MEDICATIONS": "uncovered_medications",
            "COVERED_PROCEDURES": "covered_procedures",
            "UNCOVERED_PROCEDURES": "uncovered_procedures",
            "COVERED_IMMUNIZATIONS": "covered_immunizations",
            "UNCOVERED_IMMUNIZATIONS": "uncovered_immunizations",
            "UNIQUE_CUSTOMERS": "unique_customers",
            "QOLS_AVG": "qols_avg",
            "MEMBER_MONTHS": "member_months",
        },

        "foreign_keys": {},
        "date_columns": [],
    },


    "providers": {
        "source_file": "providers.csv",
        "target_table": "providers",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "ORGANIZATION": "organization_id",
            "NAME": "name",
            "GENDER": "gender",
            "SPECIALITY": "speciality",
            "ADDRESS": "address",
            "CITY": "city",
            "STATE": "state",
            "ZIP": "zip",
            "LAT": "latitude",
            "LON": "longitude",
            "UTILIZATION": "utilization",
        },

        "foreign_keys": {
            "organization_id": {
                "table": "organizations",
                "column": "id",
            }
        },

        "date_columns": [],
    },


    "encounters": {
        "source_file": "encounters.csv",
        "target_table": "encounters",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "START": "start_time",
            "STOP": "stop_time",
            "PATIENT": "patient_id",
            "ORGANIZATION": "organization_id",
            "PROVIDER": "provider_id",
            "PAYER": "payer_id",
            "ENCOUNTERCLASS": "encounter_class",
            "CODE": "code",
            "DESCRIPTION": "description",
            "BASE_ENCOUNTER_COST": "base_encounter_cost",
            "TOTAL_CLAIM_COST": "total_claim_cost",
            "PAYER_COVERAGE": "payer_coverage",
            "REASONCODE": "reason_code",
            "REASONDESCRIPTION": "reason_description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "organization_id": {
                "table": "organizations",
                "column": "id",
            },
            "provider_id": {
                "table": "providers",
                "column": "id",
            },
            "payer_id": {
                "table": "payers",
                "column": "id",
            },
        },

        "date_columns": [
            "start_time",
            "stop_time",
        ],
    },


    "conditions": {
        "source_file": "conditions.csv",
        "target_table": "conditions",
        "primary_key": "generated",

        "column_mapping": {
            "START": "start_date",
            "STOP": "stop_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "start_date",
            "stop_date",
        ],
    },


    "allergies": {
        "source_file": "allergies.csv",
        "target_table": "allergies",
        "primary_key": "generated",

        "column_mapping": {
            "START": "start_date",
            "STOP": "stop_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "start_date",
            "stop_date",
        ],
    },


    "observations": {
        "source_file": "observations.csv",
        "target_table": "observations",
        "primary_key": "generated",

        "column_mapping": {
            "DATE": "observation_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
            "VALUE": "value",
            "UNITS": "units",
            "TYPE": "observation_type",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "observation_date",
        ],
    },


    "medications": {
        "source_file": "medications.csv",
        "target_table": "medications",
        "primary_key": "generated",

        "column_mapping": {
            "START": "start_date",
            "STOP": "stop_date",
            "PATIENT": "patient_id",
            "PAYER": "payer_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
            "BASE_COST": "base_cost",
            "PAYER_COVERAGE": "payer_coverage",
            "DISPENSES": "dispenses",
            "TOTALCOST": "total_cost",
            "REASONCODE": "reason_code",
            "REASONDESCRIPTION": "reason_description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "payer_id": {
                "table": "payers",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "start_date",
            "stop_date",
        ],
    },


    "procedures": {
        "source_file": "procedures.csv",
        "target_table": "procedures",
        "primary_key": "generated",

        "column_mapping": {
            "DATE": "procedure_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
            "BASE_COST": "base_cost",
            "REASONCODE": "reason_code",
            "REASONDESCRIPTION": "reason_description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "procedure_date",
        ],
    },


    "careplans": {
        "source_file": "careplans.csv",
        "target_table": "careplans",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "START": "start_date",
            "STOP": "stop_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
            "REASONCODE": "reason_code",
            "REASONDESCRIPTION": "reason_description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "start_date",
            "stop_date",
        ],
    },


    "devices": {
        "source_file": "devices.csv",
        "target_table": "devices",
        "primary_key": "generated",

        "column_mapping": {
            "START": "start_date",
            "STOP": "stop_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
            "UDI": "udi",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "start_date",
            "stop_date",
        ],
    },


    "imaging_studies": {
        "source_file": "imaging_studies.csv",
        "target_table": "imaging_studies",
        "primary_key": "id",

        "column_mapping": {
            "Id": "id",
            "DATE": "study_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "BODYSITE_CODE": "body_site_code",
            "BODYSITE_DESCRIPTION": "body_site_description",
            "MODALITY_CODE": "modality_code",
            "MODALITY_DESCRIPTION": "modality_description",
            "SOP_CODE": "sop_code",
            "SOP_DESCRIPTION": "sop_description",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "study_date",
        ],
    },


    "immunizations": {
        "source_file": "immunizations.csv",
        "target_table": "immunizations",
        "primary_key": "generated",

        "column_mapping": {
            "DATE": "immunization_date",
            "PATIENT": "patient_id",
            "ENCOUNTER": "encounter_id",
            "CODE": "code",
            "DESCRIPTION": "description",
            "BASE_COST": "base_cost",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "encounter_id": {
                "table": "encounters",
                "column": "id",
            },
        },

        "date_columns": [
            "immunization_date",
        ],
    },


    "payer_transitions": {
        "source_file": "payer_transitions.csv",
        "target_table": "payer_transitions",
        "primary_key": "generated",

        "column_mapping": {
            "PATIENT": "patient_id",
            "START_YEAR": "start_year",
            "END_YEAR": "end_year",
            "PAYER": "payer_id",
            "OWNERSHIP": "ownership",
        },

        "foreign_keys": {
            "patient_id": {
                "table": "patients",
                "column": "id",
            },
            "payer_id": {
                "table": "payers",
                "column": "id",
            },
        },

        "date_columns": [],
    },
}