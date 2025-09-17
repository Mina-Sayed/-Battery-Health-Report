# EV Battery Health Report

This project provides a Python-based solution for generating a battery health report from EV diagnostic JSON logs. It analyzes raw data to compute the State of Health (SOH), count charge cycles, and detect critical anomalies.

## Project Purpose

The main goal is to create a standardized, self-contained tool that can be run locally or as part of a larger vehicle diagnostics pipeline. It provides both a human-readable summary and a machine-readable JSON output for easy integration with other systems.

## How to Run

### 1. Setup Environment

Create a virtual environment and install the required dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the CLI

Execute the `battery_report.py` script, optionally providing a path to a log file. If no path is given, it defaults to `sample_log.json`.

```bash
python battery_report.py sample_log.json
```

This will print a summary to the console and generate a `battery_report_output.json` file.

**Sample CLI Output:**
```
--- Battery Health Report ---
Vehicle ID: VIN-TEST-001
Generated At: 2025-09-17T00:35:39.482892

State of Health (SOH): 71.0%
  - Method: measured_capacity
  - Confidence: high

Cycles:
  - Equivalent Full Cycles: 2.1
  - Deep Discharge Cycles: 1

Anomalies (2):
  - Type: voltage_imbalance, Severity: major, Value: 0.11
  - Type: overheating, Severity: critical, Value: 61
```

### 3. Run the API (Optional)

The project includes an optional FastAPI server to expose the report generation functionality via a REST API.

```bash
uvicorn api:app --reload
```

You can then send a `POST` request with the log data to `http://127.0.0.1:8000/v1/battery_report`.

### 4. Run Tests

To ensure the correctness of the logic, run the included pytest unit tests.

```bash
pytest
```

## Production Considerations

For a production environment, this solution should be enhanced with the following:

- **Asynchronous Processing**: Use background workers (e.g., Celery, RQ) to handle report generation asynchronously, preventing API timeouts for large logs.
- **Data Storage**: Store raw logs in a scalable object store like Amazon S3 and the generated reports in a structured database like PostgreSQL for querying and analysis.
- **Monitoring & Alerting**: Integrate with monitoring tools (e.g., Prometheus, Grafana) to track system performance and set up alerts for critical anomalies.
- **Input Validation & Security**: Implement robust input validation to handle malformed data and protect against security vulnerabilities.
- **Per-Vendor Calibration**: Calibrate SOH algorithms and anomaly thresholds for different vehicle makes and models, as battery chemistries and reporting standards can vary.
