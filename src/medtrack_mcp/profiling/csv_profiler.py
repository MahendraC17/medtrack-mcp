from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_ROOT / "data" / "source" / "synthea"
OUTPUT_DIR = PROJECT_ROOT / "data" / "baseline"
OUTPUT_FILE = OUTPUT_DIR / "profile.json"


def profile_csv(file_path):
    df = pd.read_csv(file_path)

    profile = {
        "file_name": file_path.name,
        "table_name": file_path.stem,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "null_counts": {
            column: int(count)
            for column, count in df.isnull().sum().items()
        },
        "duplicate_rows": int(df.duplicated().sum()),
    }

    return profile


def profile_all_csvs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset_profile = {}

    for file_path in sorted(SOURCE_DIR.glob("*.csv")):
        print(f"Profiling {file_path.name}...")
        dataset_profile[file_path.stem] = profile_csv(file_path)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(dataset_profile, file, indent=4)
    print(f"\nProfile saved to: {OUTPUT_FILE}")

    return dataset_profile


if __name__ == "__main__":
    profile_all_csvs()