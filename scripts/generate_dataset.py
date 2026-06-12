
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# Generate a realistic simulated cloud activity log dataset
def generate_dataset():
    """
    Generate a demo cloud activity log dataset with injected anomalies.

    Returns:
        pandas.DataFrame: Generated dataset
    """

    print("[INFO] Initializing dataset generation...")

    try:
        # Initialize Faker and NumPy random generator
        fake = Faker()
        rng = np.random.default_rng(seed=42)

        # Define dataset size
        total_rows = 500

        # Define users
        users = [f"USER{i:03d}" for i in range(1, 11)]

        # Define actions and probabilities
        actions = [
            "GetObject",
            "PutObject",
            "ListBuckets",
            "LoginAttempt",
            "DescribeInstances",
            "DeleteObject",
            "CreateInstance",
            "TerminateInstance"
        ]

        action_weights = [
            0.30,
            0.20,
            0.15,
            0.15,
            0.10,
            0.05,
            0.03,
            0.02
        ]

        # Define resources
        resources = [
            "S3_bucket_prod",
            "EC2_instance_01",
            "RDS_database",
            "IAM_role_admin",
            "Lambda_function_01"
        ]

        # Define user locations
        city_mapping = {
            "USER001": "Mumbai",
            "USER002": "Delhi",
            "USER003": "Bangalore",
            "USER004": "Chennai",
            "USER005": "Hyderabad",
            "USER006": "Pune",
            "USER007": "Kolkata",
            "USER008": "Ahmedabad",
            "USER009": "Jaipur",
            "USER010": "Lucknow"
        }

        # Generate a consistent home IP for each user
        user_ip_mapping = {}

        for user in users:
            user_ip_mapping[user] = fake.ipv4_public()

        # Define date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        print("[INFO] Generating base records...")

        records = []

        # Generate roughly equal user distribution
        user_assignments = np.repeat(users, total_rows // len(users))

        while len(user_assignments) < total_rows:
            user_assignments = np.append(
                user_assignments,
                rng.choice(users)
            )

        rng.shuffle(user_assignments)

        # Generate records
        for user_id in user_assignments:

            # Generate timestamps
            random_days = int(rng.integers(0, 90))

            base_date = start_date + timedelta(days=random_days)

            # USER007 night anomaly preparation
            if user_id == "USER007":
                hour = int(rng.integers(1, 21))
            else:
                outside_hours = rng.random() < 0.15

                if outside_hours:
                    hour = int(
                        rng.choice(
                            list(range(0, 7)) + list(range(21, 24))
                        )
                    )
                else:
                    hour = int(rng.integers(7, 21))

            minute = int(rng.integers(0, 60))
            second = int(rng.integers(0, 60))

            timestamp = base_date.replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=0
            )

            record = {
                "user_id": user_id,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "action": rng.choice(actions, p=action_weights),
                "resource": rng.choice(resources),
                "ip_address": user_ip_mapping[user_id],
                "location": city_mapping[user_id],
                "data_volume_mb": round(
                    float(rng.uniform(1.0, 50.0)),
                    2
                ),
                "status": rng.choice(
                    ["success", "failed"],
                    p=[0.90, 0.10]
                )
            }

            records.append(record)

        # Convert to DataFrame
        df = pd.DataFrame(records)

        print("[INFO] Injecting anomalies...")

        # --------------------------------------------------
        # USER007 NIGHT-TIME ACCESS ANOMALY (15 rows)
        # --------------------------------------------------
        user007_indices = df[
            df["user_id"] == "USER007"
        ].sample(
            n=15,
            random_state=42
        ).index

        for idx in user007_indices:

            current_timestamp = pd.to_datetime(
                df.loc[idx, "timestamp"]
            )

            night_hour = int(rng.integers(1, 5))

            current_timestamp = current_timestamp.replace(
                hour=night_hour
            )

            df.loc[idx, "timestamp"] = current_timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # --------------------------------------------------
        # USER009 FOREIGN IP + LOCATION ANOMALY (8 rows)
        # --------------------------------------------------
        user009_indices = df[
            df["user_id"] == "USER009"
        ].sample(
            n=8,
            random_state=42
        ).index

        foreign_ips = [
            f"185.220.{rng.integers(0,255)}.{rng.integers(1,255)}"
            if i < 4
            else f"1.180.{rng.integers(0,255)}.{rng.integers(1,255)}"
            for i in range(8)
        ]

        foreign_locations = [
            "Russia",
            "Russia",
            "Russia",
            "Russia",
            "China",
            "China",
            "China",
            "China"
        ]

        for idx, ip, location in zip(
            user009_indices,
            foreign_ips,
            foreign_locations
        ):
            df.loc[idx, "ip_address"] = ip
            df.loc[idx, "location"] = location

        # --------------------------------------------------
        # USER003 DATA EXFILTRATION ANOMALY (3 rows)
        # --------------------------------------------------
        user003_indices = df[
            df["user_id"] == "USER003"
        ].sample(
            n=3,
            random_state=42
        ).index

        for idx in user003_indices:
            df.loc[idx, "data_volume_mb"] = round(
                float(rng.uniform(1000.0, 2000.0)),
                2
            )

        # --------------------------------------------------
        # USER005 BRUTE FORCE SIMULATION
        # --------------------------------------------------
        user005_indices = df[
            df["user_id"] == "USER005"
        ].index[:12]

        df.loc[user005_indices, "status"] = "failed"

        # --------------------------------------------------
        # Save dataset
        # --------------------------------------------------
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

        print("[SUCCESS] Dataset saved successfully.")
        print(f"[INFO] Output file: {output_file}")

        # --------------------------------------------------
        # Dataset overview
        # --------------------------------------------------
        print("\n" + "=" * 60)
        print("DATASET INFORMATION")
        print("=" * 60)

        print(f"\nShape: {df.shape}")

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 5 Rows:")
        print(df.head())

        # --------------------------------------------------
        # Anomaly validation summary
        # --------------------------------------------------
        print("\n" + "=" * 60)
        print("INJECTED ANOMALY SUMMARY")
        print("=" * 60)

        night_rows = df[
            (df["user_id"] == "USER007")
            &
            (
                pd.to_datetime(df["timestamp"]).dt.hour.between(1, 4)
            )
        ]

        print(
            f"USER007 night activity rows: "
            f"{len(night_rows)}"
        )

        foreign_rows = df[
            (df["user_id"] == "USER009")
            &
            (
                df["location"].isin(
                    ["Russia", "China"]
                )
            )
        ]

        print(
            f"USER009 foreign access rows: "
            f"{len(foreign_rows)}"
        )

        exfiltration_rows = df[
            df["data_volume_mb"] >= 1000
        ]

        print(
            f"USER003 large data transfer rows: "
            f"{len(exfiltration_rows)}"
        )

        brute_force_rows = df[
            (df["user_id"] == "USER005")
            &
            (df["status"] == "failed")
        ]

        print(
            f"USER005 failed login rows: "
            f"{len(brute_force_rows)}"
        )

        print("\n[SUCCESS] Dataset generation completed.")

        return df

    except Exception as error:
        print(f"[ERROR] Dataset generation failed: {error}")
        raise


# Main execution entry point
def main():
    print("[INFO] Starting Script 01 - Dataset Generator")
    generate_dataset()


if __name__ == "__main__":
    main()
 
