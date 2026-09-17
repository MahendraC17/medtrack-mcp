from sqlalchemy import text

from medtrack_mcp.database.connection import engine


RECORDS_TO_SELECT = 80
SOURCE_START = "2010-01-01"
SOURCE_END = "2017-12-31"
TARGET_MONTH = "2018-03-01"


def inject_mt001():
    print("\n" + "=" * 60)
    print("MT-001: ENCOUNTER DATE SPIKE")
    print("=" * 60)

    select_query = text("""
        SELECT id, start_time, stop_time
        FROM encounters
        WHERE start_time >= :source_start
        AND start_time < :source_end
        ORDER BY RANDOM()
        LIMIT :records_to_select
    """)

    update_query = text("""
        UPDATE encounters
        SET start_time = :new_start,
            stop_time = :new_stop
        WHERE id = :encounter_id
    """)

    with engine.begin() as connection:

        selected_records = connection.execute(
            select_query,
            {
                "source_start": SOURCE_START,
                "source_end": SOURCE_END,
                "records_to_select": RECORDS_TO_SELECT
            }
        ).fetchall()

        if len(selected_records) != RECORDS_TO_SELECT:
            raise RuntimeError(
                f"Expected {RECORDS_TO_SELECT} records, "
                f"but selected {len(selected_records)}."
            )

        target_year = int(TARGET_MONTH[:4])
        target_month = int(TARGET_MONTH[5:7])

        for record in selected_records:

            encounter_id = record.id
            original_start = record.start_time
            original_stop = record.stop_time

            new_start = original_start.replace(
                year=target_year,
                month=target_month
            )

            new_stop = None

            if original_stop is not None:
                new_stop = original_stop.replace(
                    year=target_year,
                    month=target_month
                )

            connection.execute(
                update_query,
                {
                    "new_start": new_start,
                    "new_stop": new_stop,
                    "encounter_id": encounter_id
                }
            )

    print(f"Records moved: {len(selected_records)}")
    print(f"Target month: {TARGET_MONTH}")
    print("MT-001 injection successful.")


if __name__ == "__main__":
    inject_mt001()