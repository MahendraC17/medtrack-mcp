from mcp.server import MCPServer

from medtrack_mcp.mcp.tools import (
    detect_encounter_volume_anomalies,
    investigate_detected_encounter_volume,
)


mcp = MCPServer("MedTrack")


@mcp.tool()
def detect_encounter_volume_anomalies_tool():
    """
    Detect abnormal monthly encounter volume.
    """

    return detect_encounter_volume_anomalies()


@mcp.tool()
def investigate_encounter_volume_tool(
    anomaly_event: dict
):
    """
    Investigate a detected encounter volume anomaly.
    """

    return investigate_detected_encounter_volume(
        anomaly_event
    )


if __name__ == "__main__":
    mcp.run()