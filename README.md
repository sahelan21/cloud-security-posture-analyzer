# Cloud Security Posture Analyzer Using AI-Driven Anomaly Detection

A lightweight open-source cloud security monitoring tool built for Indian Small and Medium Enterprises (SMEs). Analyzes cloud activity logs, detects suspicious behavior using machine learning, and presents findings through automated reports and visualizations.

> BCA Final Year Major Project, Amity University Online, Cloud and Security Elective (TCS-aligned curriculum)

---

## The Problem

Enterprise cloud security tools like Microsoft Sentinel and AWS GuardDuty cost thousands of dollars monthly and require dedicated security teams. Indian SMEs have no affordable alternative and remain completely blind to threats in their own cloud environments.

---

## What This Tool Does

- Ingests real or simulated AWS CloudTrail style cloud activity logs
- Cleans and engineers features for machine learning analysis
- Detects anomalies using Scikit-learn Isolation Forest algorithm
- Stores results in SQLite for structured querying
- Generates visualizations for pattern analysis
- Produces automated threat reports with severity scoring and recommended actions

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Core language |
| Pandas | Data cleaning and feature engineering |
| Scikit-learn | Isolation Forest anomaly detection |
| Matplotlib and Seaborn | Visualizations |
| SQLite3 | Database storage and querying |
| Faker | Synthetic data generation |
| Power BI | Interactive dashboard |

---

## Installation

git clone https://github.com/sahelan21/cloud-security-posture-analyzer.git

cd cloud-security-posture-analyzer

pip install -r requirements.txt

---

## How To Run

**Demo mode (no data needed):**
python scripts/generate_dataset.py
python scripts/data_ingestion.py
python scripts/clean_and_engineer.py
python scripts/anomaly_detection.py
python scripts/sql_database.py
python scripts/visualizations.py
python scripts/alert_report.py

**Your own CSV file:**
python scripts/data_ingestion.py --file yourfile.csv

**AWS CloudTrail JSON:**
python scripts/data_ingestion.py --file cloudtrail.json --format cloudtrail

---

## Security Patterns Detected

- Unusual login times such as late night activity
- Logins from unexpected geographic locations
- Unusually large data downloads in a single session
- Repeated failed login attempts indicating brute force
- Access to high risk resources by low privilege users

---

## Academic Context

Student: Mohammed Sahelan
Institution: Amity University Online
Program: Bachelor of Computer Applications
Year: 2025 to 2026

---

## License

MIT License. Free to use, modify, and distribute with attribution.