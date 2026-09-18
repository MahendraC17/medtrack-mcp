from medtrack_mcp.detection.encounter_volume import (
    detect_anomalies,
    get_monthly_encounter_volume,
)
from medtrack_mcp.investigation.encounter_volume import (
    investigate_encounter_volume,
)


def detect_encounter_volume_anomalies():
    """
    Detect abnormal monthly encounter volume.

    Returns:
        List of anomaly events requiring investigation.
    """

    df = get_monthly_encounter_volume()

    return detect_anomalies(df)


def investigate_detected_encounter_volume(anomaly_event):
    """
    Investigate a detected encounter volume anomaly.

    Args:
        anomaly_event: An anomaly event returned by
            detect_encounter_volume_anomalies().

    Returns:
        Investigation evidence for the anomaly.
    """

    return investigate_encounter_volume(
        anomaly_event
    )