 
import os
import json
import argparse
import importlib.util

import pandas as pd


# Define the required dataset schema
REQUIRED_COLUMNS = [
    "user_id",
    "timestamp",
    "action",
    "resource",
    "ip_address",
    "location",
    "data_volume_mb",
    "status"
]


# Display a column mapping guide for users
def print_column_mapping_guide():
    """
    Print a user-friendly mapping guide when required
    columns are missing from the uploaded dataset.
    """

    print("\n[ERROR] Required columns are missing.\n")

    print("Please rename your columns to match the following schema:\n")

    mapping_guide = {
        "user_id": "Unique user identifier",
        "timestamp": "Date and time of activity",
        "action": "Activity performed",
        "resource": "Cloud resource accessed",
        "ip_address": "Source IP address",
        "location": "City, country, or region",
        "data_volume_mb": "Data transferred in MB",
        "status": "success or failed"
    }

    for column_name, description in mapping_guide.items():
        print(f"{column_name:<20} {description}")

    print("\nExample:")
    print("username -> user_id")
    print("event_time -> timestamp")
    print("event_type -> action")


# Save dataframe to standard raw_logs.csv location
def save_dataset(df):
    """
    Save dataset to the standard project location.
    """

    project_root = os.getcwd()

    output_file = os.path.join(
        project_root,
        "data",
        "raw_logs.csv"
    )

    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    df.to_csv(output_file, index=False)

    print(f"\n[INFO] Total rows loaded: {len(df)}")
    print("[SUCCESS] Dataset saved to data/raw_logs.csv")


# Handle demo mode generation
def run_demo_mode():
    """
    Generate a simulated dataset using generate_dataset.py
    """

    print(
        "No data file provided. Running in demo mode "
        "with simulated dataset."
    )

    try:
        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        generator_path = os.path.join(
            current_dir,
            "generate_dataset.py"
        )

        spec = importlib.util.spec_from_file_location(
            "generate_dataset_module",
            generator_path
        )

        dataset_module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(dataset_module)

        dataset_module.generate_dataset()

        print(
            "[SUCCESS] data/raw_logs.csv is ready."
        )

    except Exception as error:
        print(
            f"[ERROR] Failed to generate demo dataset: "
            f"{error}"
        )


# Handle user CSV upload
def process_csv_file(file_path):
    """
    Load and validate a user-supplied CSV file.
    """

    print("[INFO] Loading CSV file...")

    try:
        df = pd.read_csv(file_path)

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:

            print(
                "\n[ERROR] Missing columns detected:"
            )

            for column in missing_columns:
                print(f" - {column}")

            print_column_mapping_guide()

            return

        # Fill missing string values
        string_columns = [
            "user_id",
            "action",
            "resource",
            "ip_address",
            "location",
            "status"
        ]

        for column in string_columns:
            df[column] = df[column].fillna("unknown")

        # Fill missing numeric values
        df["data_volume_mb"] = (
            df["data_volume_mb"]
            .fillna(0)
        )

        # Standardize status values
        df["status"] = (
            df["status"]
            .astype(str)
            .str.lower()
        )

        save_dataset(df)

    except FileNotFoundError:
        print("[ERROR] File not found.")

    except Exception as error:
        print(
            f"[ERROR] Failed to process CSV: "
            f"{error}"
        )


# Convert CloudTrail records into project schema
def process_cloudtrail_json(file_path):
    """
    Parse AWS CloudTrail JSON logs and map them
    into the project's standard schema.
    """

    print("[INFO] Loading CloudTrail JSON...")

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as json_file:

            cloudtrail_data = json.load(json_file)

        records = cloudtrail_data.get(
            "Records",
            []
        )

        transformed_records = []

        for record in records:

            user_name = (
                record
                .get("userIdentity", {})
                .get("userName")
            )

            if not user_name:
                user_name = "unknown_user"

            request_parameters = record.get(
                "requestParameters",
                {}
            )

            resource = str(
                request_parameters
            )[:50]

            status = (
                "failed"
                if record.get("errorCode")
                else "success"
            )

            transformed_record = {
                "user_id": user_name,
                "timestamp": record.get(
                    "eventTime",
                    ""
                ),
                "action": record.get(
                    "eventName",
                    ""
                ),
                "resource": resource,
                "ip_address": record.get(
                    "sourceIPAddress",
                    "unknown"
                ),
                "location": record.get(
                    "awsRegion",
                    "unknown"
                ),
                "data_volume_mb": 0.0,
                "status": status
            }

            transformed_records.append(
                transformed_record
            )

        df = pd.DataFrame(
            transformed_records,
            columns=REQUIRED_COLUMNS
        )

        save_dataset(df)

    except FileNotFoundError:
        print("[ERROR] File not found.")

    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON file.")

    except Exception as error:
        print(
            f"[ERROR] Failed to process "
            f"CloudTrail logs: {error}"
        )


# Main program entry point
def main():

    print(
        "[INFO] Starting Data Ingestion Module..."
    )

    parser = argparse.ArgumentParser(
        description=(
            "Cloud Security Posture Analyzer "
            "Data Ingestion Tool"
        )
    )

    parser.add_argument(
        "--file",
        help="Path to input dataset"
    )

    parser.add_argument(
        "--format",
        choices=["csv", "cloudtrail"],
        default="csv",
        help="Input file format"
    )

    args = parser.parse_args()

    # Scenario 1: Demo mode
    if not args.file:
        run_demo_mode()
        return

    # Scenario 2: CSV upload
    if args.format == "csv":
        process_csv_file(args.file)

    # Scenario 3: CloudTrail JSON
    elif args.format == "cloudtrail":
        process_cloudtrail_json(args.file)


if __name__ == "__main__":
    main()
