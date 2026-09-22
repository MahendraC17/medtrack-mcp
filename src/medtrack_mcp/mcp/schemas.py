from pydantic import BaseModel, Field


class EncounterVolumeInvestigationRequest(BaseModel):
    anomaly_type: str = Field(
        description="The detected anomaly type."
    )
    metric: str = Field(
        description="The metric associated with the anomaly."
    )
    period_start: str = Field(
        description="Start date of the anomalous period in YYYY-MM-DD format."
    )
    period_end: str = Field(
        description="End date of the anomalous period in YYYY-MM-DD format."
    )
    period: str = Field(
        description="Anomalous period in YYYY-MM format."
    )


class PatientEncounterFrequencyInvestigationRequest(BaseModel):
    anomaly_type: str = Field(
        description="The detected anomaly type."
    )
    metric: str = Field(
        description="The metric associated with the anomaly."
    )
    patient_id: str = Field(
        description="Patient identifier associated with the anomaly."
    )
    period_start: str = Field(
        description="Start date of the anomalous period in YYYY-MM-DD format."
    )
    period_end: str = Field(
        description="End date of the anomalous period in YYYY-MM-DD format."
    )
    period: str = Field(
        description="Anomalous period in YYYY-MM format."
    )
    observed_value: int = Field(
        description="Observed encounter count for the anomalous period."
    )