
import os
from datetime import datetime

import pandas as pd


# Generate reason text for an anomaly
def generate_reason(row):
    """
    Build explanation text based on anomaly indicators.
    """

    reasons = []

    if row["is_night_login"] == 1:
        reasons.append(
            "after-hours login detected"
        )

    if row["is_foreign_location"] == 1:
        reasons.append(
            "foreign location detected"
        )

    if row["data_volume_mb"] > 500:
        reasons.append(
            "unusually large data transfer"
        )

    if row["is_failed"] == 1:
        reasons.append(
            "failed authentication attempt"
        )

    if not reasons:
        return "behavior deviates from normal baseline"

    return ", ".join(reasons)


# Generate recommendation based on severity
def generate_recommendation(
    severity,
    reason_text
):
    """
    Create recommendation text.
    """

    if severity == "High":

        return (
            "SUSPEND ACCOUNT IMMEDIATELY. "
            f"{reason_text}. "
            "Escalate to security team."
        )

    elif severity == "Medium":

        return (
            "MONITOR CLOSELY. "
            "Verify with user directly. "
            f"{reason_text}. "
            "Review in 24 hours."
        )

    else:

        return (
            "LOG AND REVIEW. "
            "Flag for weekly audit. "
            f"{reason_text}. "
            "No immediate action."
        )


# Build report content
def generate_report():
    """
    Generate security alert report.
    """

    try:

        # ------------------------------------------
        # Build file paths
        # ------------------------------------------
        project_root = os.getcwd()

        input_file = os.path.join(
            project_root,
            "outputs",
            "anomaly_results.csv"
        )

        output_file = os.path.join(
            project_root,
            "outputs",
            "alert_report.txt"
        )

        print(
            "[INFO] Loading anomaly results..."
        )

        # ------------------------------------------
        # Load data
        # ------------------------------------------
        df = pd.read_csv(input_file)

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        total_logs = len(df)

        anomaly_df = df[
            df["anomaly_label"] == "Anomaly"
        ].copy()

        anomaly_df = anomaly_df.sort_values(
            by="anomaly_score",
            ascending=True
        )

        total_anomalies = len(
            anomaly_df
        )

        anomaly_percent = (
            total_anomalies
            / total_logs
        ) * 100

        # ------------------------------------------
        # Executive summary metrics
        # ------------------------------------------
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

        user_counts = (
            anomaly_df.groupby(
                "user_id"
            )
            .size()
            .sort_values(
                ascending=False
            )
        )

        if len(user_counts) > 0:
            most_at_risk_user = (
                user_counts.index[0]
            )
        else:
            most_at_risk_user = "N/A"

        hour_counts = (
            anomaly_df.groupby(
                "hour_of_day"
            )
            .size()
            .sort_values(
                ascending=False
            )
        )

        if len(hour_counts) > 0:
            peak_hour = (
                hour_counts.index[0]
            )
        else:
            peak_hour = "N/A"

        foreign_incidents = len(
            anomaly_df[
                anomaly_df[
                    "is_foreign_location"
                ] == 1
            ]
        )

        # ------------------------------------------
        # Build report
        # ------------------------------------------
        report_lines = []

        report_lines.append(
            "=" * 50
        )

        report_lines.append(
            "CLOUD SECURITY POSTURE ANALYZER"
        )

        report_lines.append(
            "Automated Threat Detection Report"
        )

        report_lines.append(
            f"Generated: {datetime.now()}"
        )

        report_lines.append(
            "=" * 50
        )

        report_lines.append("")

        report_lines.append(
            "--- EXECUTIVE SUMMARY ---"
        )

        report_lines.append(
            f"Total Logs Analyzed: "
            f"{total_logs}"
        )

        report_lines.append(
            f"Total Anomalies Detected: "
            f"{total_anomalies} "
            f"({anomaly_percent:.1f} percent)"
        )

        report_lines.append(
            f"High Severity: {high_count}"
        )

        report_lines.append(
            f"Medium Severity: {medium_count}"
        )

        report_lines.append(
            f"Low Severity: {low_count}"
        )

        report_lines.append(
            f"Most At-Risk User: "
            f"{most_at_risk_user}"
        )

        report_lines.append(
            f"Peak Suspicious Hour: "
            f"{peak_hour}"
        )

        report_lines.append(
            f"Foreign Location Incidents: "
            f"{foreign_incidents}"
        )

        report_lines.append(
            "-" * 50
        )

        report_lines.append("")

        # ------------------------------------------
        # Incident section
        # ------------------------------------------
        for incident_number, (
            _,
            row
        ) in enumerate(
            anomaly_df.iterrows(),
            start=1
        ):

            severity = (
                row["severity"]
                .upper()
            )

            reason_text = generate_reason(
                row
            )

            recommendation = (
                generate_recommendation(
                    row["severity"],
                    reason_text
                )
            )

            report_lines.append(
                f"[INCIDENT #{incident_number:03d}] "
                f"[{severity}]"
            )

            report_lines.append(
                f"Timestamp   : "
                f"{row['timestamp']}"
            )

            report_lines.append(
                f"User        : "
                f"{row['user_id']}"
            )

            report_lines.append(
                f"Action      : "
                f"{row['action']}"
            )

            report_lines.append(
                f"Resource    : "
                f"{row['resource']}"
            )

            report_lines.append(
                f"Location    : "
                f"{row['location']}"
            )

            report_lines.append(
                f"IP Address  : "
                f"{row['ip_address']}"
            )

            report_lines.append(
                f"Data Volume : "
                f"{row['data_volume_mb']} MB"
            )

            report_lines.append(
                f"Risk Score  : "
                f"{row['anomaly_score']:.4f}"
            )

            report_lines.append(
                f"Recommended : "
                f"{recommendation}"
            )

            report_lines.append(
                "-" * 50
            )

        # ------------------------------------------
        # Footer
        # ------------------------------------------
        report_lines.append("")

        report_lines.append(
            "=" * 50
        )

        report_lines.append(
            "END OF REPORT"
        )

        report_lines.append(
            "Cloud Security Posture Analyzer v1.0"
        )

        report_lines.append(
            "Built for Indian SMEs as an open source security monitoring solution"
        )

        report_lines.append(
            "=" * 50
        )

        report_text = "\n".join(
            report_lines
        )

        # ------------------------------------------
        # Save report
        # ------------------------------------------
        os.makedirs(
            os.path.dirname(
                output_file
            ),
            exist_ok=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as report_file:

            report_file.write(
                report_text
            )

        # ------------------------------------------
        # Print to console
        # ------------------------------------------
        print("\n")
        print(report_text)

        print(
            "\nAlert report saved to outputs/alert_report.txt"
        )

    except FileNotFoundError:

        print(
            "[ERROR] outputs/anomaly_results.csv not found."
        )

    except Exception as error:

        print(
            f"[ERROR] Report generation failed: "
            f"{error}"
        )


# Main execution function
def main():

    print(
        "[INFO] Starting Alert Report Generator..."
    )

    generate_report()


if __name__ == "__main__":
    main()
