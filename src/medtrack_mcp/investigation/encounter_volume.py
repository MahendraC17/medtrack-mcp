import pandas as pd
from sqlalchemy import text

from medtrack_mcp.database.connection import engine
from medtrack_mcp.detection.encounter_volume import (
    detect_encounter_volume_anomalies,
    get_monthly_encounter_volume,
)


BASELINE_START = "2010-01-01"
BASELINE_END = "2018-01-01"

TOP_N = 10


def get_month_encounter_volume(month_start, month_end):

    query = text("""
        SELECT
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE start_time >= :month_start
        AND start_time < :month_end
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "month_start": month_start,
                "month_end": month_end
            }
        )

        return result.scalar()


def get_historical_monthly_volume(month_number):

    query = text("""
        SELECT
            EXTRACT(YEAR FROM start_time) AS year,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE start_time >= :baseline_start
        AND start_time < :baseline_end
        AND EXTRACT(MONTH FROM start_time) = :month_number
        GROUP BY EXTRACT(YEAR FROM start_time)
        ORDER BY year
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "baseline_start": BASELINE_START,
                "baseline_end": BASELINE_END,
                "month_number": month_number
            }
        ).fetchall()

    return pd.DataFrame(
        rows,
        columns=["year", "encounter_count"]
    )


def get_organization_breakdown(month_start, month_end):

    query = text("""
        SELECT
            o.id AS organization_id,
            o.name AS organization,
            COUNT(*) AS encounter_count
        FROM encounters e
        JOIN organizations o
            ON e.organization_id = o.id
        WHERE e.start_time >= :month_start
        AND e.start_time < :month_end
        GROUP BY
            o.id,
            o.name
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "month_start": month_start,
                "month_end": month_end
            }
        ).fetchall()

    return pd.DataFrame(
        rows,
        columns=[
            "organization_id",
            "organization",
            "encounter_count"
        ]
    )


def get_encounter_type_breakdown(month_start, month_end):

    query = text("""
        SELECT
            encounter_class,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE start_time >= :month_start
        AND start_time < :month_end
        GROUP BY encounter_class
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "month_start": month_start,
                "month_end": month_end
            }
        ).fetchall()

    return pd.DataFrame(
        rows,
        columns=[
            "encounter_class",
            "encounter_count"
        ]
    )


def get_provider_breakdown(month_start, month_end):

    query = text("""
        SELECT
            p.id AS provider_id,
            p.name AS provider,
            p.speciality,
            COUNT(*) AS encounter_count
        FROM encounters e
        JOIN providers p
            ON e.provider_id = p.id
        WHERE e.start_time >= :month_start
        AND e.start_time < :month_end
        GROUP BY
            p.id,
            p.name,
            p.speciality
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "month_start": month_start,
                "month_end": month_end
            }
        ).fetchall()

    return pd.DataFrame(
        rows,
        columns=[
            "provider_id",
            "provider",
            "speciality",
            "encounter_count"
        ]
    )


def get_patient_summary(month_start, month_end):

    query = text("""
        SELECT
            COUNT(*) AS encounter_count,
            COUNT(DISTINCT patient_id) AS unique_patients,
            ROUND(
                COUNT(*)::numeric
                / NULLIF(COUNT(DISTINCT patient_id), 0),
                2
            ) AS encounters_per_patient
        FROM encounters
        WHERE start_time >= :month_start
        AND start_time < :month_end
    """)

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {
                "month_start": month_start,
                "month_end": month_end
            }
        ).fetchone()

    return {
        "encounter_count": row.encounter_count,
        "unique_patients": row.unique_patients,
        "encounters_per_patient": (
            float(row.encounters_per_patient)
            if row.encounters_per_patient is not None
            else None
        )
    }


def get_encounter_records(month_start, month_end):

    query = text("""
        SELECT
            e.id AS encounter_id,
            e.start_time,
            e.stop_time,
            e.patient_id,
            e.organization_id,
            o.name AS organization,
            e.provider_id,
            p.name AS provider,
            p.speciality,
            e.encounter_class,
            e.code,
            e.description,
            e.reason_code,
            e.reason_description
        FROM encounters e
        LEFT JOIN organizations o
            ON e.organization_id = o.id
        LEFT JOIN providers p
            ON e.provider_id = p.id
        WHERE e.start_time >= :month_start
        AND e.start_time < :month_end
        ORDER BY e.start_time, e.id
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "month_start": month_start,
                "month_end": month_end
            }
        ).fetchall()

    return pd.DataFrame(
        rows,
        columns=[
            "encounter_id",
            "start_time",
            "stop_time",
            "patient_id",
            "organization_id",
            "organization",
            "provider_id",
            "provider",
            "speciality",
            "encounter_class",
            "code",
            "description",
            "reason_code",
            "reason_description"
        ]
    )


def investigate_encounter_volume(anomaly_event):

    if anomaly_event["anomaly_type"] != "encounter_volume":
        raise ValueError(
            "Unsupported anomaly type for encounter volume investigation."
        )

    month_start = pd.Timestamp(
        anomaly_event["period_start"]
    )

    month_end = pd.Timestamp(
        anomaly_event["period_end"]
    )

    month_number = month_start.month

    observed_volume = get_month_encounter_volume(
        month_start,
        month_end
    )

    historical_volume = get_historical_monthly_volume(
        month_number
    )

    organization_breakdown = get_organization_breakdown(
        month_start,
        month_end
    )

    encounter_type_breakdown = get_encounter_type_breakdown(
        month_start,
        month_end
    )

    provider_breakdown = get_provider_breakdown(
        month_start,
        month_end
    )

    patient_summary = get_patient_summary(
        month_start,
        month_end
    )

    historical_mean = (
        historical_volume["encounter_count"].mean()
        if not historical_volume.empty
        else None
    )

    historical_deviation = None

    if historical_mean is not None and historical_mean != 0:
        historical_deviation = (
            (
                observed_volume - historical_mean
            )
            / historical_mean
            * 100
        )

    return {
        "anomaly": anomaly_event,

        "investigation_period": {
            "start": month_start.strftime("%Y-%m-%d"),
            "end": month_end.strftime("%Y-%m-%d")
        },

        "encounter_volume": {
            "observed": observed_volume,
            "historical_mean": (
                round(historical_mean, 2)
                if historical_mean is not None
                else None
            ),
            "historical_deviation_pct": (
                round(historical_deviation, 2)
                if historical_deviation is not None
                else None
            ),
            "historical_monthly_volume": (
                historical_volume.to_dict("records")
            )
        },

        "organization_breakdown": (
            organization_breakdown
            .head(TOP_N)
            .to_dict("records")
        ),

        "encounter_type_breakdown": (
            encounter_type_breakdown
            .to_dict("records")
        ),

        "provider_breakdown": (
            provider_breakdown
            .head(TOP_N)
            .to_dict("records")
        ),

        "patient_summary": patient_summary
    }


def print_investigation(result):

    anomaly = result["anomaly"]
    period = result["investigation_period"]
    volume = result["encounter_volume"]

    print("\n" + "=" * 60)
    print("ENCOUNTER VOLUME INVESTIGATION")
    print("=" * 60)

    print(
        f"\nAnomaly type: "
        f"{anomaly['anomaly_type']}"
    )

    print(
        f"Investigation period: "
        f"{period['start']} to {period['end']}"
    )

    print("\nENCOUNTER VOLUME")
    print("-" * 60)

    print(
        f"Observed encounters: "
        f"{volume['observed']}"
    )

    print(
        f"Historical monthly mean: "
        f"{volume['historical_mean']}"
    )

    print(
        f"Deviation from historical mean: "
        f"{volume['historical_deviation_pct']:+.2f}%"
    )

    print("\nHISTORICAL SAME-MONTH VOLUME")
    print("-" * 60)

    for row in volume["historical_monthly_volume"]:
        print(
            f"{int(row['year'])}: "
            f"{int(row['encounter_count'])}"
        )

    print("\nTOP ORGANIZATIONS")
    print("-" * 60)

    for row in result["organization_breakdown"]:
        print(
            f"{row['organization']}: "
            f"{row['encounter_count']}"
        )

    print("\nENCOUNTER TYPES")
    print("-" * 60)

    for row in result["encounter_type_breakdown"]:
        print(
            f"{row['encounter_class']}: "
            f"{row['encounter_count']}"
        )

    print("\nTOP PROVIDERS")
    print("-" * 60)

    for row in result["provider_breakdown"]:
        print(
            f"{row['provider']} "
            f"({row['speciality']}): "
            f"{row['encounter_count']}"
        )

    print("\nPATIENT SUMMARY")
    print("-" * 60)

    patient_summary = result["patient_summary"]

    print(
        f"Unique patients: "
        f"{patient_summary['unique_patients']}"
    )

    print(
        f"Encounters per patient: "
        f"{patient_summary['encounters_per_patient']}"
    )


if __name__ == "__main__":

    detection_df = get_monthly_encounter_volume()

    anomaly_events = detect_encounter_volume_anomalies(
        detection_df
    )

    if not anomaly_events:
        print("No anomalies available for investigation.")
    else:
        for anomaly_event in anomaly_events:

            result = investigate_encounter_volume(
                anomaly_event
            )

            print_investigation(result)