import pandas as pd
from sqlalchemy import text

from medtrack_mcp.database.connection import engine


BASELINE_START = "2010-01-01"
BASELINE_END = "2018-01-01"


def get_patient_monthly_volume(
    patient_id,
    start_date,
    end_date,
):
    query = text("""
        SELECT
            DATE_TRUNC('month', start_time) AS month,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE patient_id = :patient_id
        AND start_time IS NOT NULL
        AND start_time >= :start_date
        AND start_time < :end_date
        GROUP BY DATE_TRUNC('month', start_time)
        ORDER BY month
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "start_date": start_date,
                "end_date": end_date,
            },
        ).fetchall()

    return pd.DataFrame(
        rows,
        columns=[
            "month",
            "encounter_count",
        ],
    )


def get_encounter_breakdown(
    patient_id,
    period_start,
    period_end,
):
    query = text("""
        SELECT
            encounter_class,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE patient_id = :patient_id
        AND start_time >= :period_start
        AND start_time < :period_end
        GROUP BY encounter_class
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "period_start": period_start,
                "period_end": period_end,
            },
        ).fetchall()

    return [
        {
            "encounter_type": row[0],
            "count": int(row[1]),
        }
        for row in rows
    ]


def get_provider_breakdown(
    patient_id,
    period_start,
    period_end,
):
    query = text("""
        SELECT
            p.name AS provider_name,
            COUNT(*) AS encounter_count
        FROM encounters e
        LEFT JOIN providers p
            ON e.provider_id = p.id
        WHERE e.patient_id = :patient_id
        AND e.start_time >= :period_start
        AND e.start_time < :period_end
        GROUP BY p.name
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "period_start": period_start,
                "period_end": period_end,
            },
        ).fetchall()

    return [
        {
            "provider": row[0],
            "count": int(row[1]),
        }
        for row in rows
    ]


def get_organization_breakdown(
    patient_id,
    period_start,
    period_end,
):
    query = text("""
        SELECT
            o.name AS organization_name,
            COUNT(*) AS encounter_count
        FROM encounters e
        LEFT JOIN organizations o
            ON e.organization_id = o.id
        WHERE e.patient_id = :patient_id
        AND e.start_time >= :period_start
        AND e.start_time < :period_end
        GROUP BY o.name
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "period_start": period_start,
                "period_end": period_end,
            },
        ).fetchall()

    return [
        {
            "organization": row[0],
            "count": int(row[1]),
        }
        for row in rows
    ]


def get_encounter_code_breakdown(
    patient_id,
    period_start,
    period_end,
):
    query = text("""
        SELECT
            code,
            description,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE patient_id = :patient_id
        AND start_time >= :period_start
        AND start_time < :period_end
        GROUP BY code, description
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "period_start": period_start,
                "period_end": period_end,
            },
        ).fetchall()

    return [
        {
            "code": row[0],
            "description": row[1],
            "count": int(row[2]),
        }
        for row in rows
    ]


def get_reason_breakdown(
    patient_id,
    period_start,
    period_end,
):
    query = text("""
        SELECT
            reason_code,
            reason_description,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE patient_id = :patient_id
        AND start_time >= :period_start
        AND start_time < :period_end
        AND reason_description IS NOT NULL
        GROUP BY reason_code, reason_description
        ORDER BY encounter_count DESC
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "period_start": period_start,
                "period_end": period_end,
            },
        ).fetchall()

    return [
        {
            "reason_code": row[0],
            "reason": row[1],
            "count": int(row[2]),
        }
        for row in rows
    ]


def get_daily_activity(
    patient_id,
    period_start,
    period_end,
):
    query = text("""
        SELECT
            DATE(start_time) AS encounter_date,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE patient_id = :patient_id
        AND start_time >= :period_start
        AND start_time < :period_end
        GROUP BY DATE(start_time)
        ORDER BY encounter_date
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "patient_id": patient_id,
                "period_start": period_start,
                "period_end": period_end,
            },
        ).fetchall()

    return [
        {
            "date": row[0].isoformat(),
            "count": int(row[1]),
        }
        for row in rows
    ]


def investigate_patient_encounter_frequency(
    anomaly_event,
):
    if anomaly_event["anomaly_type"] != (
        "patient_encounter_frequency"
    ):
        raise ValueError(
            "Unsupported anomaly type for "
            "patient encounter frequency investigation."
        )

    patient_id = anomaly_event["patient_id"]

    period_start = pd.Timestamp(
        anomaly_event["period_start"]
    )

    period_end = pd.Timestamp(
        anomaly_event["period_end"]
    )

    historical_end = period_start

    monthly_volume = get_patient_monthly_volume(
        patient_id,
        BASELINE_START,
        BASELINE_END,
    )

    if not monthly_volume.empty:
        monthly_volume["month"] = (
            pd.to_datetime(monthly_volume["month"])
            .dt.tz_localize(None)
        )

    historical_mean = (
        monthly_volume["encounter_count"].mean()
        if not monthly_volume.empty
        else None
    )

    return {
        "anomaly": anomaly_event,

        "investigation_period": {
            "start": period_start.strftime(
                "%Y-%m-%d"
            ),
            "end": period_end.strftime(
                "%Y-%m-%d"
            ),
        },

        "patient": {
            "patient_id": patient_id,
        },

        "encounter_volume": {
            "observed": anomaly_event[
                "observed_value"
            ],
            "historical_mean": (
                round(float(historical_mean), 2)
                if historical_mean is not None
                else None
            ),
            "historical_monthly_volume": [
                {
                    "month": row["month"].strftime(
                        "%Y-%m"
                    ),
                    "count": int(
                        row["encounter_count"]
                    ),
                }
                for _, row in monthly_volume.iterrows()
            ],
        },

        "encounter_type_breakdown": (
            get_encounter_breakdown(
                patient_id,
                period_start,
                period_end,
            )
        ),

        "provider_breakdown": (
            get_provider_breakdown(
                patient_id,
                period_start,
                period_end,
            )
        ),

        "organization_breakdown": (
            get_organization_breakdown(
                patient_id,
                period_start,
                period_end,
            )
        ),

        "encounter_code_breakdown": (
            get_encounter_code_breakdown(
                patient_id,
                period_start,
                period_end,
            )
        ),

        "reason_breakdown": (
            get_reason_breakdown(
                patient_id,
                period_start,
                period_end,
            )
        ),

        "daily_activity": (
            get_daily_activity(
                patient_id,
                period_start,
                period_end,
            )
        ),
    }


def print_investigation(result):
    print("\n" + "=" * 60)
    print("PATIENT ENCOUNTER FREQUENCY INVESTIGATION")
    print("=" * 60)

    anomaly = result["anomaly"]

    print(
        f"\nPatient: "
        f"{anomaly['patient_id']}"
    )

    print(
        f"Period: "
        f"{anomaly['period']}"
    )

    print("\nENCOUNTER VOLUME")
    print("-" * 60)

    print(
        f"Observed: "
        f"{result['encounter_volume']['observed']}"
    )

    print(
        f"Historical mean: "
        f"{result['encounter_volume']['historical_mean']}"
    )

    print("\nENCOUNTER TYPES")
    print("-" * 60)

    for item in result["encounter_type_breakdown"]:
        print(
            f"{item['encounter_type']}: "
            f"{item['count']}"
        )

    print("\nPROVIDERS")
    print("-" * 60)

    for item in result["provider_breakdown"]:
        print(
            f"{item['provider']}: "
            f"{item['count']}"
        )

    print("\nORGANIZATIONS")
    print("-" * 60)

    for item in result["organization_breakdown"]:
        print(
            f"{item['organization']}: "
            f"{item['count']}"
        )

    print("\nENCOUNTER CODES")
    print("-" * 60)

    for item in result["encounter_code_breakdown"]:
        print(
            f"{item['code']} | "
            f"{item['description']}: "
            f"{item['count']}"
        )

    print("\nREASONS")
    print("-" * 60)

    if not result["reason_breakdown"]:
        print("No recorded encounter reasons.")

    for item in result["reason_breakdown"]:
        print(
            f"{item['reason']}: "
            f"{item['count']}"
        )

    print("\nDAILY ACTIVITY")
    print("-" * 60)

    for item in result["daily_activity"]:
        print(
            f"{item['date']}: "
            f"{item['count']}"
        )


if __name__ == "__main__":
    from medtrack_mcp.detection.patient_encounter_frequency import (
        detect_patient_encounter_frequency_anomalies,
        get_monthly_patient_encounters,
    )

    df = get_monthly_patient_encounters()
    events = detect_patient_encounter_frequency_anomalies(df)

    for event in events:
        result = investigate_patient_encounter_frequency(
            event
        )
        print_investigation(result)