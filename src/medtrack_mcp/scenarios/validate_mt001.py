from sqlalchemy import text

from medtrack_mcp.database.connection import engine


EXPECTED_BASELINE_COUNT = 240
EXPECTED_INJECTED_RECORDS = 80
EXPECTED_COUNT = (
    EXPECTED_BASELINE_COUNT +
    EXPECTED_INJECTED_RECORDS
)

TARGET_START = "2018-03-01"
TARGET_END = "2018-04-01"


def get_target_count():
    query = text("""
        SELECT COUNT(*)
        FROM encounters
        WHERE start_time >= :target_start
        AND start_time < :target_end
    """)

    with engine.connect() as connection:
        return connection.execute(
            query,
            {
                "target_start": TARGET_START,
                "target_end": TARGET_END
            }
        ).scalar()


def validate_mt001():
    print("\n" + "=" * 60)
    print("MT-001 VALIDATION")
    print("=" * 60)

    actual_count = get_target_count()

    print(f"Baseline target count: {EXPECTED_BASELINE_COUNT}")
    print(f"Expected injected records: {EXPECTED_INJECTED_RECORDS}")
    print(f"Expected target count: {EXPECTED_COUNT}")
    print(f"Actual target count: {actual_count}")

    if actual_count == EXPECTED_COUNT:
        print("\nMT-001 VALIDATION SUCCESSFUL")
        return True

    print("\nMT-001 VALIDATION FAILED")
    return False


if __name__ == "__main__":
    validate_mt001()