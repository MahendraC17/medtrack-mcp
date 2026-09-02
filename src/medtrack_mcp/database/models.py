from sqlalchemy import Column, Integer, Numeric, String, Text, ForeignKey, Date, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True)

    birth_date = Column(Date)
    death_date = Column(Date)

    ssn = Column(String)
    drivers_license = Column(String)
    passport = Column(String)

    prefix = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    suffix = Column(String)
    maiden_name = Column(String)

    marital_status = Column(String)
    race = Column(String)
    ethnicity = Column(String)
    gender = Column(String)

    birthplace = Column(Text)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    county = Column(String)
    zip = Column(String)

    latitude = Column(Numeric(10, 6))
    longitude = Column(Numeric(10, 6))

    healthcare_expenses = Column(Numeric(14, 2))
    healthcare_coverage = Column(Numeric(14, 2))


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True)

    name = Column(Text)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip = Column(String)

    latitude = Column(Numeric(10, 6))
    longitude = Column(Numeric(10, 6))

    phone = Column(String)

    revenue = Column(Numeric(14, 2))
    utilization = Column(Integer)


class Payer(Base):
    __tablename__ = "payers"

    id = Column(String(36), primary_key=True)

    name = Column(Text)
    address = Column(Text)
    city = Column(String)
    state_headquartered = Column(String)
    zip = Column(String)
    phone = Column(String)

    amount_covered = Column(Numeric(14, 2))
    amount_uncovered = Column(Numeric(14, 2))
    revenue = Column(Numeric(14, 2))

    covered_encounters = Column(Integer)
    uncovered_encounters = Column(Integer)

    covered_medications = Column(Integer)
    uncovered_medications = Column(Integer)

    covered_procedures = Column(Integer)
    uncovered_procedures = Column(Integer)

    covered_immunizations = Column(Integer)
    uncovered_immunizations = Column(Integer)

    unique_customers = Column(Integer)
    qols_avg = Column(Numeric(10, 4))
    member_months = Column(Integer)

class Provider(Base):
    __tablename__ = "providers"

    id = Column(String(36), primary_key=True)

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id")
    )

    name = Column(Text)
    gender = Column(String)
    speciality = Column(String)

    address = Column(Text)
    city = Column(String)
    state = Column(String)
    zip = Column(String)

    latitude = Column(Numeric(10, 6))
    longitude = Column(Numeric(10, 6))

    utilization = Column(Integer)


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(String(36), primary_key=True)

    start_time = Column(DateTime)
    stop_time = Column(DateTime)

    patient_id = Column(
        String(36),
        ForeignKey("patients.id")
    )

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id")
    )

    provider_id = Column(
        String(36),
        ForeignKey("providers.id")
    )

    payer_id = Column(
        String(36),
        ForeignKey("payers.id")
    )

    encounter_class = Column(String)
    code = Column(String)
    description = Column(Text)

    base_encounter_cost = Column(Numeric(14, 2))
    total_claim_cost = Column(Numeric(14, 2))
    payer_coverage = Column(Numeric(14, 2))

    reason_code = Column(String)
    reason_description = Column(Text)


class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    start_date = Column(Date)
    stop_date = Column(Date)

    patient_id = Column(
        String(36),
        ForeignKey("patients.id")
    )

    encounter_id = Column(
        String(36),
        ForeignKey("encounters.id")
    )

    code = Column(String)
    description = Column(Text)


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, autoincrement=True)

    start_date = Column(Date)
    stop_date = Column(Date)

    patient_id = Column(
        String(36),
        ForeignKey("patients.id")
    )

    encounter_id = Column(
        String(36),
        ForeignKey("encounters.id")
    )

    code = Column(String)
    description = Column(Text)


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    observation_date = Column(DateTime)

    patient_id = Column(
        String(36),
        ForeignKey("patients.id")
    )

    encounter_id = Column(
        String(36),
        ForeignKey("encounters.id")
    )

    code = Column(String)
    description = Column(Text)

    value = Column(Text)
    units = Column(String)
    observation_type = Column(String)

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    start_date = Column(Date)
    stop_date = Column(Date)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    payer_id = Column(String(36), ForeignKey("payers.id"))
    encounter_id = Column(String(36), ForeignKey("encounters.id"))

    code = Column(String)
    description = Column(Text)

    base_cost = Column(Numeric(14, 2))
    payer_coverage = Column(Numeric(14, 2))
    dispenses = Column(Integer)
    total_cost = Column(Numeric(14, 2))

    reason_code = Column(String)
    reason_description = Column(Text)


class Procedure(Base):
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, autoincrement=True)

    procedure_date = Column(Date)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    encounter_id = Column(String(36), ForeignKey("encounters.id"))

    code = Column(String)
    description = Column(Text)

    base_cost = Column(Numeric(14, 2))

    reason_code = Column(String)
    reason_description = Column(Text)


class Careplan(Base):
    __tablename__ = "careplans"

    id = Column(String(36), primary_key=True)

    start_date = Column(Date)
    stop_date = Column(Date)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    encounter_id = Column(String(36), ForeignKey("encounters.id"))

    code = Column(String)
    description = Column(Text)

    reason_code = Column(String)
    reason_description = Column(Text)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)

    start_date = Column(Date)
    stop_date = Column(Date)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    encounter_id = Column(String(36), ForeignKey("encounters.id"))

    code = Column(String)
    description = Column(Text)
    udi = Column(Text)


class Immunization(Base):
    __tablename__ = "immunizations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    immunization_date = Column(Date)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    encounter_id = Column(String(36), ForeignKey("encounters.id"))

    code = Column(String)
    description = Column(Text)

    base_cost = Column(Numeric(14, 2))

class ImagingStudy(Base):
    __tablename__ = "imaging_studies"

    id = Column(String(36), primary_key=True)

    study_date = Column(DateTime)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    encounter_id = Column(String(36), ForeignKey("encounters.id"))

    body_site_code = Column(String)
    body_site_description = Column(Text)

    modality_code = Column(String)
    modality_description = Column(Text)

    sop_code = Column(String)
    sop_description = Column(Text)


class PayerTransition(Base):
    __tablename__ = "payer_transitions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    patient_id = Column(String(36), ForeignKey("patients.id"))
    payer_id = Column(String(36), ForeignKey("payers.id"))

    start_year = Column(Integer)
    end_year = Column(Integer)

    ownership = Column(String)