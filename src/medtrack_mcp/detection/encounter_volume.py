import pandas as pd
from sqlalchemy import text

from medtrack_mcp.database.connection import engine


BASELINE_START = "2010-01-01"
BASELINE_END = "2018-01-01"

DETECTION_START = "2018-01-01"
DETECTION_END = "2019-01-01"

PCT_DEVIATION_THRESHOLD = 20.0
MONTHLY_CHANGE_THRESHOLD = 50.0


def get_monthly_encounter_volume():

    query = text("""
        SELECT
            DATE_TRUNC('month', start_time) AS month,
            COUNT(*) AS encounter_count
        FROM encounters
        WHERE start_time IS NOT NULL
        AND start_time >= :start_date
        AND start_time < :end_date
        GROUP BY DATE_TRUNC('month', start_time)
        ORDER BY month
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {
                "start_date": BASELINE_START,
                "end_date": DETECTION_END
            }
        ).fetchall()

    df = pd.DataFrame(
        rows,
        columns=["month", "encounter_count"]
    )

    if df.empty:
        raise RuntimeError("No encounter data found.")

    df["month"] = pd.to_datetime(df["month"])

    return df


def calculate_baseline(df):

    baseline = df[
        (df["month"] >= pd.Timestamp(BASELINE_START))
        & (df["month"] < pd.Timestamp(BASELINE_END))
    ]

    if baseline.empty:
        raise RuntimeError("No baseline encounter data found.")

    return baseline["encounter_count"].mean()


def detect_anomalies(df):

    baseline_mean = calculate_baseline(df)

    detection = df[
        (df["month"] >= pd.Timestamp(DETECTION_START))
        & (df["month"] < pd.Timestamp(DETECTION_END))
    ].copy()

    detection["baseline_mean"] = baseline_mean

    detection["pct_deviation"] = (
        (
            detection["encounter_count"]
            - detection["baseline_mean"]
        )
        / detection["baseline_mean"]
        * 100
    )

    detection["pct_change"] = (
        detection["encounter_count"]
        .pct_change()
        .mul(100)
    )

    anomaly_events = []

    for _, row in detection.iterrows():

        reasons = []

        if row["pct_deviation"] >= PCT_DEVIATION_THRESHOLD:
            reasons.append(
                f"encounter volume deviation of "
                f"{row['pct_deviation']:+.2f}% from baseline"
            )

        if (
            not pd.isna(row["pct_change"])
            and row["pct_change"] >= MONTHLY_CHANGE_THRESHOLD
        ):
            reasons.append(
                f"month-to-month change of "
                f"{row['pct_change']:+.2f}%"
            )

        if not reasons:
            continue

        period_start = row["month"]
        period_end = period_start + pd.DateOffset(months=1)

        anomaly_events.append(
            {
                "anomaly_type": "encounter_volume",
                "metric": "monthly_encounter_volume",

                "period_start": period_start.strftime(
                    "%Y-%m-%d"
                ),
                "period_end": period_end.strftime(
                    "%Y-%m-%d"
                ),

                "period": period_start.strftime("%Y-%m"),

                "observed_value": int(
                    row["encounter_count"]
                ),
                "baseline_value": round(
                    row["baseline_mean"],
                    2
                ),
                "deviation_pct": round(
                    row["pct_deviation"],
                    2
                ),
                "month_to_month_change_pct": (
                    None
                    if pd.isna(row["pct_change"])
                    else round(row["pct_change"], 2)
                ),

                "reasons": reasons,
                "status": "requires_investigation"
            }
        )

    return anomaly_events


def run_detection():

    df = get_monthly_encounter_volume()

    anomaly_events = detect_anomalies(df)

    print("\n" + "=" * 60)
    print("ENCOUNTER VOLUME DETECTION")
    print("=" * 60)

    print(
        f"Baseline: {BASELINE_START} to {BASELINE_END}"
    )

    print(
        f"Detection period: "
        f"{DETECTION_START} to {DETECTION_END}"
    )

    print(
        f"\nAnomalies detected: "
        f"{len(anomaly_events)}"
    )

    if not anomaly_events:
        print("\nNo encounter volume anomalies detected.")
        return []

    print("\nDETECTION EVENTS")
    print("-" * 60)

    for event in anomaly_events:

        print(
            "\nALERT: Encounter volume anomaly detected"
        )

        print(
            f"Period: {event['period']}"
        )

        print(
            f"Observed encounters: "
            f"{event['observed_value']}"
        )

        print(
            f"Historical baseline: "
            f"{event['baseline_value']}"
        )

        print(
            f"Deviation: "
            f"{event['deviation_pct']:+.2f}%"
        )

        if event["month_to_month_change_pct"] is not None:
            print(
                f"Month-to-month change: "
                f"{event['month_to_month_change_pct']:+.2f}%"
            )

        print("Reasons:")

        for reason in event["reasons"]:
            print(f"  - {reason}")

        print(
            f"Status: {event['status']}"
        )

    return anomaly_events


if __name__ == "__main__":
    run_detection()