import pandas as pd
from sqlalchemy import text

from medtrack_mcp.database.connection import engine


BASELINE_START = "2010-01-01"
BASELINE_END = "2018-01-01"

DETECTION_START = "2018-01-01"
DETECTION_END = "2019-01-01"

MIN_ENCOUNTERS = 10
MULTIPLIER_THRESHOLD = 5.0


def get_monthly_patient_encounters():
    query = text("""
        SELECT
            patient_id,
            DATE_TRUNC('month', start_time) AS month,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE start_time IS NOT NULL
        AND start_time >= :baseline_start
        AND start_time < :detection_end
        GROUP BY
            patient_id,
            DATE_TRUNC('month', start_time)
        ORDER BY
            patient_id,
            month
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "baseline_start": BASELINE_START,
                "detection_end": DETECTION_END,
            },
        ).fetchall()

    df = pd.DataFrame(
        rows,
        columns=[
            "patient_id",
            "month",
            "encounter_count",
        ],
    )

    if df.empty:
        raise RuntimeError(
            "No patient encounter data found."
        )

    df["month"] = (
        pd.to_datetime(df["month"])
        .dt.tz_localize(None)
    )

    return df


def calculate_patient_baselines(df):
    baseline_df = df[
        (df["month"] >= pd.Timestamp(BASELINE_START))
        & (df["month"] < pd.Timestamp(BASELINE_END))
    ]

    return (
        baseline_df
        .groupby("patient_id")["encounter_count"]
        .mean()
        .rename("baseline_mean")
        .reset_index()
    )


def detect_anomalies(df):
    baseline = calculate_patient_baselines(df)

    detection_df = df[
        (df["month"] >= pd.Timestamp(DETECTION_START))
        & (df["month"] < pd.Timestamp(DETECTION_END))
    ].copy()

    detection_df = detection_df.merge(
        baseline,
        on="patient_id",
        how="inner",
    )

    detection_df["multiple_of_baseline"] = (
        detection_df["encounter_count"]
        / detection_df["baseline_mean"]
    )

    anomalies = detection_df[
        (detection_df["encounter_count"] >= MIN_ENCOUNTERS)
        & (
            detection_df["multiple_of_baseline"]
            >= MULTIPLIER_THRESHOLD
        )
    ].copy()

    events = []

    for _, row in anomalies.iterrows():

        period_start = row["month"]
        period_end = period_start + pd.offsets.MonthBegin(1)

        events.append(
            {
                "anomaly_type": (
                    "patient_encounter_frequency"
                ),
                "metric": (
                    "monthly_patient_encounter_volume"
                ),
                "patient_id": row["patient_id"],
                "period_start": (
                    period_start.strftime("%Y-%m-%d")
                ),
                "period_end": (
                    period_end.strftime("%Y-%m-%d")
                ),
                "period": period_start.strftime("%Y-%m"),
                "observed_value": int(
                    row["encounter_count"]
                ),
                "baseline_value": round(
                    float(row["baseline_mean"]),
                    2,
                ),
                "multiple_of_baseline": round(
                    float(row["multiple_of_baseline"]),
                    2,
                ),
                "reasons": [
                    (
                        f"patient had "
                        f"{int(row['encounter_count'])} "
                        f"encounters in one month"
                    ),
                    (
                        f"monthly volume was "
                        f"{row['multiple_of_baseline']:.2f}x "
                        f"the patient's historical mean"
                    ),
                ],
                "status": "requires_investigation",
            }
        )

    return events


def print_detection(events):
    print("\n" + "=" * 60)
    print("PATIENT ENCOUNTER FREQUENCY DETECTION")
    print("=" * 60)

    print(
        f"Baseline: "
        f"{BASELINE_START} to {BASELINE_END}"
    )

    print(
        f"Detection period: "
        f"{DETECTION_START} to {DETECTION_END}"
    )

    print(f"\nAnomalies detected: {len(events)}")

    for event in events:
        print("\nALERT: Patient encounter frequency anomaly")
        print("-" * 60)
        print(f"Patient: {event['patient_id']}")
        print(f"Period: {event['period']}")
        print(
            f"Observed encounters: "
            f"{event['observed_value']}"
        )
        print(
            f"Historical baseline: "
            f"{event['baseline_value']}"
        )
        print(
            f"Multiple of baseline: "
            f"{event['multiple_of_baseline']:.2f}x"
        )
        print("Reasons:")

        for reason in event["reasons"]:
            print(f"  - {reason}")

        print(f"Status: {event['status']}")


if __name__ == "__main__":
    df = get_monthly_patient_encounters()
    events = detect_anomalies(df)
    print_detection(events)