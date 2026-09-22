from mcp.server import MCPServer

from medtrack_mcp.mcp.tools import (
    detect_encounter_volume_anomalies,
    investigate_detected_encounter_volume,
    detect_patient_encounter_frequency_anomalies,
    investigate_detected_patient_encounter_frequency,
)

from medtrack_mcp.mcp.schemas import (
    EncounterVolumeInvestigationRequest,
    PatientEncounterFrequencyInvestigationRequest,
)


mcp = MCPServer("MedTrack")


@mcp.tool()
def detect_encounter_volume_anomalies_tool():
    """
    Detect abnormal monthly encounter volume.
    """

    return detect_encounter_volume_anomalies()


@mcp.tool()
def investigate_encounter_volume_tool(request: EncounterVolumeInvestigationRequest):
    """
    Investigate a detected encounter volume anomaly.
    """

    return investigate_detected_encounter_volume(request.model_dump())

@mcp.tool()
def detect_patient_encounter_frequency_anomalies_tool():
    """
    Detect abnormal patient encounter frequency.
    """

    return detect_patient_encounter_frequency_anomalies()


@mcp.tool()
def investigate_patient_encounter_frequency_tool(request: PatientEncounterFrequencyInvestigationRequest):
    """
    Investigate a detected patient encounter frequency anomaly.
    """

    return investigate_detected_patient_encounter_frequency(request.model_dump())

if __name__ == "__main__":
    mcp.run()