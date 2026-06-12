
import os

import numpy as np
import pandas as pd


# Define trusted Indian locations for foreign access detection
INDIAN_LOCATIONS = [
    "mumbai",
    "delhi",
    "bangalore",
    "chennai",
    "hyderabad",
    "pune",
    "kolkata",
    "ahmedabad",
    "jaipur",
    "lucknow"
]


# Load, clean, and engineer features from raw logs
def clean_and_engineer():
    """
    Load raw logs, clean the dataset,
    engineer anomaly detection features,
    and save the processed dataset.
    """

    try:
        # Build input file path
        project_root = os.getcwd()

        input_file = os.path.join(
            project_root,
            "data",
            "raw_logs.csv"
        )

        output_file = os.path.join(
            project_root,
            "data",
            "cleaned_logs.csv"
        )

        print("[INFO] Loading raw dataset...")

        # Load raw dataset
        df = pd.read_csv(input_file)

        print(f"[INFO] Initial Shape: {df.shape}")
        print(f"[INFO] Columns: {list(df.columns)}")

        # --------------------------------------------------
        # Parse timestamps and remove invalid rows
        # --------------------------------------------------
        print(
            "[INFO] Converting timestamp column "
            "to datetime..."
        )

        original_row_count = len(df)

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df = df.dropna(subset=["timestamp"])

        invalid_timestamp_rows = (
            original_row_count - len(df)
        )

        print(
            f"[INFO] Dropped "
            f"{invalid_timestamp_rows} "
            f"rows with invalid timestamps."
        )

        # --------------------------------------------------
        # Remove whitespace from string columns
        # --------------------------------------------------
        print(
            "[INFO] Stripping whitespace "
            "from string columns..."
        )

        string_columns = df.select_dtypes(
            include=["object"]
        ).columns

        for column in string_columns:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )

        # --------------------------------------------------
        # Standardize text columns
        # --------------------------------------------------
        print(
            "[INFO] Standardizing action, "
            "status, and location..."
        )

        for column in [
            "action",
            "status",
            "location"
        ]:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .astype(str)
                    .str.lower()
                )

        # --------------------------------------------------
        # Fill missing string values
        # --------------------------------------------------
        print(
            "[INFO] Filling missing "
            "string values..."
        )

        string_columns = [
            column
            for column in df.columns
            if df[column].dtype == "object"
        ]

        for column in string_columns:

            df[column] = (
                df[column]
                .replace(
                    ["", "nan", "None"],
                    np.nan
                )
                .fillna("unknown")
            )

        # --------------------------------------------------
        # Fill missing numeric values
        # --------------------------------------------------
        print(
            "[INFO] Filling missing "
            "numeric values..."
        )

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        for column in numeric_columns:

            df[column] = (
                df[column]
                .fillna(0)
            )

        # --------------------------------------------------
        # Remove exact duplicate rows
        # --------------------------------------------------
        print(
            "[INFO] Removing duplicate rows..."
        )

        rows_before_dedup = len(df)

        df = df.drop_duplicates()

        duplicate_rows_removed = (
            rows_before_dedup - len(df)
        )

        print(
            f"[INFO] Removed "
            f"{duplicate_rows_removed} "
            f"duplicate rows."
        )

        # --------------------------------------------------
        # Create hour_of_day feature
        # --------------------------------------------------
        print(
            "[INFO] Engineering features..."
        )

        df["hour_of_day"] = (
            df["timestamp"]
            .dt.hour
        )

        # --------------------------------------------------
        # Create day_of_week feature
        # --------------------------------------------------
        df["day_of_week"] = (
            df["timestamp"]
            .dt.dayofweek
        )

        # --------------------------------------------------
        # Create night login flag
        # --------------------------------------------------
        df["is_night_login"] = np.where(
            (
                (df["hour_of_day"] >= 22)
                |
                (df["hour_of_day"] <= 5)
            ),
            1,
            0
        )

        # --------------------------------------------------
        # Create foreign location flag
        # --------------------------------------------------
        df["is_foreign_location"] = np.where(
            ~df["location"].isin(
                INDIAN_LOCATIONS
            ),
            1,
            0
        )

        # --------------------------------------------------
        # Create failed status flag
        # --------------------------------------------------
        df["is_failed"] = np.where(
            df["status"] == "failed",
            1,
            0
        )

        # --------------------------------------------------
        # Count actions performed by user
        # --------------------------------------------------
        df["actions_per_user"] = (
            df.groupby("user_id")[
                "user_id"
            ]
            .transform("count")
        )

        # --------------------------------------------------
        # Calculate average data volume
        # per user
        # --------------------------------------------------
        df["avg_data_volume_per_user"] = (
            df.groupby("user_id")[
                "data_volume_mb"
            ]
            .transform("mean")
        )

        # --------------------------------------------------
        # Count failed attempts per user
        # --------------------------------------------------
        df["failed_attempts_per_user"] = (
            df.groupby("user_id")[
                "is_failed"
            ]
            .transform("sum")
        )

        # --------------------------------------------------
        # Print statistics for engineered features
        # --------------------------------------------------
        print(
            "\n[INFO] Engineered Feature Summary"
        )

        feature_columns = [
            "hour_of_day",
            "day_of_week",
            "is_night_login",
            "is_foreign_location",
            "is_failed",
            "actions_per_user",
            "avg_data_volume_per_user",
            "failed_attempts_per_user"
        ]

        for column in feature_columns:

            print(
                f"\n{column}"
            )

            print(
                f"Mean: "
                f"{df[column].mean():.2f}"
            )

            print(
                f"Std : "
                f"{df[column].std():.2f}"
            )

        # --------------------------------------------------
        # Save cleaned dataset
        # --------------------------------------------------
        os.makedirs(
            os.path.dirname(output_file),
            exist_ok=True
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            "\n[SUCCESS] Cleaned dataset saved."
        )

        print(
            f"[INFO] Output File: "
            f"{output_file}"
        )

        print(
            f"[INFO] Final Shape: "
            f"{df.shape}"
        )

        return df

    except FileNotFoundError:

        print(
            "[ERROR] data/raw_logs.csv "
            "not found."
        )

    except Exception as error:

        print(
            f"[ERROR] Processing failed: "
            f"{error}"
        )


# Main execution function
def main():

    print(
        "[INFO] Starting Data Cleaning "
        "and Feature Engineering..."
    )

    clean_and_engineer()


if __name__ == "__main__":
    main()
