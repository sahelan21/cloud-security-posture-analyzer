
import os

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


# Define chart colors
NORMAL_COLOR = "#4A90D9"
ANOMALY_COLOR = "#E74C3C"

LOW_RISK_COLOR = "#2ECC71"
MEDIUM_RISK_COLOR = "#F39C12"
HIGH_RISK_COLOR = "#E74C3C"


# Create anomaly scatter plot
def create_anomaly_scatter(df, output_directory):
    """
    Create scatter plot of login hour
    versus data volume.
    """

    print(
        "[INFO] Creating anomaly scatter plot..."
    )

    plt.figure(figsize=(10, 6))

    for label, color in {
        "Normal": NORMAL_COLOR,
        "Anomaly": ANOMALY_COLOR
    }.items():

        subset = df[
            df["anomaly_label"] == label
        ]

        plt.scatter(
            subset["hour_of_day"],
            subset["data_volume_mb"],
            c=color,
            alpha=0.6,
            label=label
        )

    # Annotate top 3 anomaly points by data volume
    anomaly_points = (
        df[df["anomaly_label"] == "Anomaly"]
        .nlargest(
            3,
            "data_volume_mb"
        )
    )

    for _, row in anomaly_points.iterrows():

        plt.annotate(
            (
                f"{row['user_id']}\n"
                f"{row['data_volume_mb']:.1f} MB"
            ),
            (
                row["hour_of_day"],
                row["data_volume_mb"]
            ),
            fontsize=8
        )

    plt.title(
        "Cloud Activity Anomaly Detection: "
        "Data Volume vs Login Hour"
    )

    plt.xlabel("Hour of Day")

    plt.ylabel("Data Volume (MB)")

    plt.legend()

    plt.tight_layout()

    output_file = os.path.join(
        output_directory,
        "anomaly_scatter.png"
    )

    plt.savefig(
        output_file,
        dpi=150
    )

    plt.close()

    print(
        "[SUCCESS] anomaly_scatter.png saved."
    )


# Create hourly anomaly distribution chart
def create_hourly_anomalies_chart(
    df,
    output_directory
):
    """
    Create bar chart of anomaly count
    by hour of day.
    """

    print(
        "[INFO] Creating hourly anomalies chart..."
    )

    anomaly_df = df[
        df["anomaly_label"] == "Anomaly"
    ]

    hourly_counts = (
        anomaly_df.groupby(
            "hour_of_day"
        )
        .size()
        .reindex(
            range(24),
            fill_value=0
        )
    )

    bar_colors = []

    for hour in hourly_counts.index:

        if (
            0 <= hour <= 5
            or
            22 <= hour <= 23
        ):
            bar_colors.append(
                ANOMALY_COLOR
            )
        else:
            bar_colors.append(
                NORMAL_COLOR
            )

    plt.figure(figsize=(12, 6))

    bars = plt.bar(
        hourly_counts.index,
        hourly_counts.values,
        color=bar_colors
    )

    plt.title(
        "Suspicious Activity by Hour of Day"
    )

    plt.xlabel("Hour of Day")

    plt.ylabel("Anomaly Count")

    plt.xticks(range(24))

    # Add value labels
    for bar in bars:

        height = bar.get_height()

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            height,
            str(int(height)),
            ha="center",
            va="bottom",
            fontsize=8
        )

    plt.tight_layout()

    output_file = os.path.join(
        output_directory,
        "hourly_anomalies.png"
    )

    plt.savefig(
        output_file,
        dpi=150
    )

    plt.close()

    print(
        "[SUCCESS] hourly_anomalies.png saved."
    )


# Create user risk leaderboard
def create_user_risk_chart(
    df,
    output_directory
):
    """
    Create top user risk leaderboard.
    """

    print(
        "[INFO] Creating user risk chart..."
    )

    anomaly_counts = (
        df[
            df["anomaly_label"]
            == "Anomaly"
        ]
        .groupby("user_id")
        .size()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    colors = []

    for count in anomaly_counts.values:

        if count <= 2:
            colors.append(
                LOW_RISK_COLOR
            )

        elif count <= 5:
            colors.append(
                MEDIUM_RISK_COLOR
            )

        else:
            colors.append(
                HIGH_RISK_COLOR
            )

    plt.figure(figsize=(10, 6))

    bars = plt.barh(
        anomaly_counts.index,
        anomaly_counts.values,
        color=colors
    )

    plt.title(
        "User Risk Score Leaderboard"
    )

    plt.xlabel(
        "Anomaly Count"
    )

    plt.ylabel(
        "User ID"
    )

    # Add value labels
    for bar in bars:

        width = bar.get_width()

        plt.text(
            width + 0.1,
            bar.get_y()
            + bar.get_height() / 2,
            str(int(width)),
            va="center"
        )

    # Risk tier legend
    legend_elements = [
        Patch(
            facecolor=LOW_RISK_COLOR,
            label="Low Risk (0-2)"
        ),
        Patch(
            facecolor=MEDIUM_RISK_COLOR,
            label="Medium Risk (3-5)"
        ),
        Patch(
            facecolor=HIGH_RISK_COLOR,
            label="High Risk (6+)"
        )
    ]

    plt.legend(
        handles=legend_elements
    )

    plt.tight_layout()

    output_file = os.path.join(
        output_directory,
        "user_risk.png"
    )

    plt.savefig(
        output_file,
        dpi=150
    )

    plt.close()

    print(
        "[SUCCESS] user_risk.png saved."
    )


# Generate all project visualizations
def generate_visualizations():
    """
    Load anomaly results and create
    all project visualizations.
    """

    try:

        # Configure plotting style
        plt.style.use(
            "seaborn-v0_8-darkgrid"
        )

        # Build file paths
        project_root = os.getcwd()

        input_file = os.path.join(
            project_root,
            "outputs",
            "anomaly_results.csv"
        )

        output_directory = os.path.join(
            project_root,
            "outputs",
            "figures"
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        print(
            "[INFO] Loading anomaly results..."
        )

        # Load anomaly results
        df = pd.read_csv(
            input_file
        )

        # Parse timestamps
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        print(
            f"[INFO] Loaded "
            f"{len(df)} records."
        )

        # Generate all charts
        create_anomaly_scatter(
            df,
            output_directory
        )

        create_hourly_anomalies_chart(
            df,
            output_directory
        )

        create_user_risk_chart(
            df,
            output_directory
        )

        print(
            "\n[SUCCESS] All visualizations generated."
        )

        print(
            f"[INFO] Output Folder: "
            f"{output_directory}"
        )

    except FileNotFoundError:

        print(
            "[ERROR] anomaly_results.csv not found."
        )

    except Exception as error:

        print(
            f"[ERROR] Visualization generation failed: "
            f"{error}"
        )


# Main execution function
def main():

    print(
        "[INFO] Starting Visualization Module..."
    )

    generate_visualizations()


if __name__ == "__main__":
    main()
