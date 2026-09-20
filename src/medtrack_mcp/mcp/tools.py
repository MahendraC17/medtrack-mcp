from medtrack_mcp.detection.encounter_volume import (
    detect_encounter_volume_anomalies as detect_encounter_volume,
    get_monthly_encounter_volume,
)
from medtrack_mcp.investigation.encounter_volume import (
    investigate_encounter_volume,
)
from medtrack_mcp.detection.patient_encounter_frequency import (
    detect_patient_encounter_frequency_anomalies as detect_patient_encounter_frequency,
    get_monthly_patient_encounters,
)
from medtrack_mcp.investigation.patient_encounter_frequency import (
    investigate_patient_encounter_frequency,
)


def detect_encounter_volume_anomalies():
    """
    Detect abnormal monthly encounter volume.

    Returns:
        List of anomaly events requiring investigation.
    """

    df = get_monthly_encounter_volume()

    return detect_encounter_volume(df)


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


def detect_patient_encounter_frequency_anomalies():
    """
    Detect abnormal patient encounter frequency.

    Returns:
        List of patient encounter frequency anomalies
        requiring investigation.
    """
    df = get_monthly_patient_encounters()
    return detect_patient_encounter_frequency(df)


def investigate_detected_patient_encounter_frequency(anomaly_event):
    """
    Investigate a detected patient encounter frequency anomaly.

    Args:
        anomaly_event: An anomaly event returned by
            detect_patient_encounter_frequency_anomalies().

    Returns:
        Investigation evidence for the anomaly.
    """

    return investigate_patient_encounter_frequency(
        anomaly_event
    )