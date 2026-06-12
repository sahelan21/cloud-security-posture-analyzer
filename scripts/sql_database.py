
import os
import sqlite3

import pandas as pd


# Create SQLite database and run analytical queries
def create_database_and_queries():
    """
    Load anomaly results into SQLite,
    execute analytical queries,
    and print results.
    """

    connection = None

    try:
        # --------------------------------------------------
        # Build file paths
        # --------------------------------------------------
        project_root = os.getcwd()

        input_file = os.path.join(
            project_root,
            "outputs",
            "anomaly_results.csv"
        )

        database_file = os.path.join(
            project_root,
            "database",
            "security_logs.db"
        )

        print("[INFO] Loading anomaly results...")

        # --------------------------------------------------
        # Load anomaly results
        # --------------------------------------------------
        df = pd.read_csv(input_file)

        print(
            f"[INFO] Loaded {len(df)} rows."
        )

        # --------------------------------------------------
        # Parse timestamp column
        # --------------------------------------------------
        print(
            "[INFO] Parsing timestamps..."
        )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        # --------------------------------------------------
        # Create database directory
        # --------------------------------------------------
        os.makedirs(
            os.path.dirname(database_file),
            exist_ok=True
        )

        # --------------------------------------------------
        # Connect to SQLite database
        # --------------------------------------------------
        print(
            "[INFO] Creating SQLite database..."
        )

        connection = sqlite3.connect(
            database_file
        )

        cursor = connection.cursor()

        # --------------------------------------------------
        # Drop existing table
        # --------------------------------------------------
        print(
            "[INFO] Dropping existing table if present..."
        )

        cursor.execute(
            "DROP TABLE IF EXISTS cloud_logs"
        )

        connection.commit()

        # --------------------------------------------------
        # Insert data into SQLite
        # --------------------------------------------------
        print(
            "[INFO] Inserting records into database..."
        )

        df.to_sql(
            "cloud_logs",
            connection,
            if_exists="replace",
            index=False
        )

        # --------------------------------------------------
        # Verify row count
        # --------------------------------------------------
        row_count_query = """
        SELECT COUNT(*)
        AS total_rows
        FROM cloud_logs
        """

        row_count = pd.read_sql(
            row_count_query,
            connection
        )

        print(
            "\n[INFO] Row Count After Insert:"
        )

        print(row_count)

        # --------------------------------------------------
        # Query 1
        # Count anomalies by severity
        # --------------------------------------------------
        print(
            "\n=== Anomaly Count by Severity ==="
        )

        query_1 = """
        SELECT
            severity,
            COUNT(*) AS anomaly_count
        FROM cloud_logs
        WHERE anomaly_label = 'Anomaly'
        GROUP BY severity
        ORDER BY
            CASE severity
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END
        """

        result_1 = pd.read_sql(
            query_1,
            connection
        )

        print(result_1)

        # --------------------------------------------------
        # Query 2
        # Top anomaly users
        # --------------------------------------------------
        print(
            "\n=== Top 5 Users by Anomaly Count ==="
        )

        query_2 = """
        SELECT
            user_id,
            COUNT(*) AS anomaly_count
        FROM cloud_logs
        WHERE anomaly_label = 'Anomaly'
        GROUP BY user_id
        ORDER BY anomaly_count DESC
        LIMIT 5
        """

        result_2 = pd.read_sql(
            query_2,
            connection
        )

        print(result_2)

        # --------------------------------------------------
        # Query 3
        # Top suspicious hours
        # --------------------------------------------------
        print(
            "\n=== Top 5 Suspicious Hours of Day ==="
        )

        query_3 = """
        SELECT
            hour_of_day,
            COUNT(*) AS anomaly_count
        FROM cloud_logs
        WHERE anomaly_label = 'Anomaly'
        GROUP BY hour_of_day
        ORDER BY anomaly_count DESC
        LIMIT 5
        """

        result_3 = pd.read_sql(
            query_3,
            connection
        )

        print(result_3)

        # --------------------------------------------------
        # Query 4
        # Foreign location anomalies
        # --------------------------------------------------
        print(
            "\n=== Anomalies from Foreign Locations ==="
        )

        query_4 = """
        SELECT
            location,
            COUNT(*) AS anomaly_count
        FROM cloud_logs
        WHERE
            is_foreign_location = 1
            AND anomaly_label = 'Anomaly'
        GROUP BY location
        ORDER BY anomaly_count DESC
        """

        result_4 = pd.read_sql(
            query_4,
            connection
        )

        print(result_4)

        # --------------------------------------------------
        # Query 5
        # Daily anomalies last 30 days
        # --------------------------------------------------
        print(
            "\n=== Daily Anomaly Count Last 30 Days ==="
        )

        query_5 = """
        SELECT
            DATE(timestamp) AS event_date,
            COUNT(*) AS anomaly_count
        FROM cloud_logs
        WHERE
            anomaly_label = 'Anomaly'
            AND DATE(timestamp)
                >= DATE('now', '-30 day')
        GROUP BY event_date
        ORDER BY event_date ASC
        """

        result_5 = pd.read_sql(
            query_5,
            connection
        )

        print(result_5)

        print(
            "\n[SUCCESS] Database analysis complete."
        )

    except FileNotFoundError:

        print(
            "[ERROR] anomaly_results.csv not found."
        )

    except Exception as error:

        print(
            f"[ERROR] Database processing failed: "
            f"{error}"
        )

    finally:

        # --------------------------------------------------
        # Close database connection
        # --------------------------------------------------
        if connection is not None:

            connection.close()

            print(
                "[INFO] Database connection closed."
            )


# Main execution function
def main():

    print(
        "[INFO] Starting SQLite Database Module..."
    )

    create_database_and_queries()


if __name__ == "__main__":
    main()
