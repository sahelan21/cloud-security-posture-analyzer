
import os

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# Define feature columns used for anomaly detection
FEATURE_COLUMNS = [
    "hour_of_day",
    "day_of_week",
    "data_volume_mb",
    "is_night_login",
    "is_foreign_location",
    "is_failed",
    "actions_per_user",
    "avg_data_volume_per_user",
    "failed_attempts_per_user"
]


# Load engineered data and run anomaly detection
def detect_anomalies():
    """
    Train Isolation Forest and identify anomalous
    cloud activity records.
    """

    try:
        # Build file paths
        project_root = os.getcwd()

        input_file = os.path.join(
            project_root,
            "data",
            "cleaned_logs.csv"
        )

        output_file = os.path.join(
            project_root,
            "outputs",
            "anomaly_results.csv"
        )

        print("[INFO] Loading cleaned dataset...")

        # Load cleaned dataset
        df = pd.read_csv(input_file)

        print(
            f"[INFO] Dataset Shape: {df.shape}"
        )

        # ------------------------------------------
        # Select model features
        # ------------------------------------------
        print(
            "[INFO] Selecting anomaly detection features..."
        )

        feature_data = df[FEATURE_COLUMNS].copy()

        # ------------------------------------------
        # Scale features
        # ------------------------------------------
        print(
            "[INFO] Scaling features..."
        )

        scaler = StandardScaler()

        scaled_features = scaler.fit_transform(
            feature_data
        )

        # ------------------------------------------
        # Train Isolation Forest
        # ------------------------------------------
        print(
            "[INFO] Training Isolation Forest..."
        )

        isolation_forest = IsolationForest(
            contamination=0.08,
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )

        isolation_forest.fit(
            scaled_features
        )

        # ------------------------------------------
        # Generate anomaly predictions
        # ------------------------------------------
        print(
            "[INFO] Generating anomaly predictions..."
        )

        predictions = isolation_forest.predict(
            scaled_features
        )

        anomaly_scores = (
            isolation_forest.decision_function(
                scaled_features
            )
        )

        # ------------------------------------------
        # Add prediction columns
        # ------------------------------------------
        df["anomaly_score"] = anomaly_scores

        df["anomaly_label"] = predictions

        df["anomaly_label"] = df[
            "anomaly_label"
        ].map(
            {
                -1: "Anomaly",
                1: "Normal"
            }
        )

        # ------------------------------------------
        # Assign severity levels
        # ------------------------------------------
        print(
            "[INFO] Assigning severity levels..."
        )

        severity_values = []

        for _, row in df.iterrows():

            score = row["anomaly_score"]

            if row["anomaly_label"] == "Normal":
                severity = "Normal"

            elif score < -0.15:
                severity = "High"

            elif -0.15 <= score < -0.05:
                severity = "Medium"

            elif -0.05 <= score < 0:
                severity = "Low"

            else:
                severity = "Low"

            severity_values.append(
                severity
            )

        df["severity"] = severity_values

        # ------------------------------------------
        # Calculate summary metrics
        # ------------------------------------------
        total_records = len(df)

        anomaly_df = df[
            df["anomaly_label"] == "Anomaly"
        ]

        total_anomalies = len(
            anomaly_df
        )

        anomaly_percent = (
            total_anomalies
            / total_records
        ) * 100

        high_count = len(
            anomaly_df[
                anomaly_df["severity"] == "High"
            ]
        )

        medium_count = len(
            anomaly_df[
                anomaly_df["severity"] == "Medium"
            ]
        )

        low_count = len(
            anomaly_df[
                anomaly_df["severity"] == "Low"
            ]
        )

        # ------------------------------------------
        # Calculate top anomaly users
        # ------------------------------------------
        user_anomaly_counts = (
            anomaly_df.groupby(
                "user_id"
            )
            .size()
            .sort_values(
                ascending=False
            )
        )

        top_users = (
            user_anomaly_counts
            .head(5)
        )

        # ------------------------------------------
        # Print required summary
        # ------------------------------------------
        print(
            "\n=== ANOMALY DETECTION RESULTS ==="
        )

        print(
            f"Total records analyzed: "
            f"{total_records}"
        )

        print(
            f"Total anomalies flagged: "
            f"{total_anomalies} "
            f"({anomaly_percent:.1f} percent)"
        )

        print(
            f"High severity: "
            f"{high_count}"
        )

        print(
            f"Medium severity: "
            f"{medium_count}"
        )

        print(
            f"Low severity: "
            f"{low_count}"
        )

        print(
            "\nTop 5 users by anomaly count:"
        )

        for user_id, count in top_users.items():

            print(
                f"{user_id}: "
                f"{count} anomalies"
            )

        # ------------------------------------------
        # Validation checks
        # ------------------------------------------
        print(
            "\nValidation Check:"
        )

        top_user_list = (
            top_users.index.tolist()
        )

        validation_users = [
            "USER003",
            "USER005",
            "USER007",
            "USER009"
        ]

        for user_id in validation_users:

            if user_id in top_user_list:

                print(
                    f"{user_id}: PASS"
                )

            else:

                print(
                    f"{user_id}: FAIL"
                )

        # ------------------------------------------
        # Save results
        # ------------------------------------------
        print(
            "\n[INFO] Saving anomaly results..."
        )

        os.makedirs(
            os.path.dirname(
                output_file
            ),
            exist_ok=True
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            "[SUCCESS] Results saved."
        )

        print(
            f"[INFO] Output File: "
            f"{output_file}"
        )

        return df

    except FileNotFoundError:

        print(
            "[ERROR] cleaned_logs.csv not found."
        )

    except KeyError as error:

        print(
            f"[ERROR] Missing feature column: "
            f"{error}"
        )

    except Exception as error:

        print(
            f"[ERROR] Anomaly detection failed: "
            f"{error}"
        )


# Main execution function
def main():

    print(
        "[INFO] Starting Anomaly Detection..."
    )

    detect_anomalies()


if __name__ == "__main__":
    main()
 
