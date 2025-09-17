# AI Coding Assistant Instructions for EV Battery Health Report

You are an AI coding assistant for a Python project that generates battery health reports from EV diagnostic logs. Your main goal is to help developers build, maintain, and extend this service.

## 1. Big Picture Architecture

This project has two main components:
- **`battery_report.py`**: A core Python script containing all the business logic for report generation. It can be run as a standalone CLI tool.
- **`api.py`**: An optional FastAPI server that wraps the core logic in a web API endpoint.

**Data Flow:**
1. A raw JSON log (like `sample_log.json`) is provided as input.
2. `battery_report.py`'s `generate_report` function is called.
3. This function orchestrates calls to `compute_soh`, `count_cycles_from_soc`, and `detect_anomalies`.
4. The final report is returned as a dictionary and can be serialized to JSON (like `battery_report_output.json`).

## 2. Critical Developer Workflows

- **Running the CLI:**
  ```bash
  python battery_report.py [path_to_log.json]
  ```
  This is the primary way to test the core logic. It uses `sample_log.json` by default.

- **Running Tests:**
  ```bash
  pytest
  ```
  The tests in `tests/test_battery_report.py` cover the core calculation functions. Use them to validate any changes to the algorithms.

- **Running the API:**
  ```bash
  uvicorn api:app --reload
  ```
  This starts a local server. You can then `POST` a JSON log to the `/v1/battery_report` endpoint.

## 3. Project-Specific Conventions & Patterns

### State of Health (SOH) Calculation
The SOH calculation has a clear hierarchy. Always follow this order of methods:
1.  **`measured_capacity`**: If `measured_capacity_kwh` is present, use it. This is the highest confidence method.
    - `SOH = (measured_capacity_kwh / nominal_capacity_kwh) * 100`
2.  **`cycle_history_estimate`**: If no measured capacity, but `cycle_history` exists, average the `energy_kwh` from the cycles.
3.  **`voltage_heuristic`**: As a last resort, use the average cell voltage. This is a low-confidence estimate.
    - Linearly map average cell voltage from 3.2V (30% SOH) to 4.2V (100% SOH).

### Anomaly Detection
Stick to the defined thresholds in `detect_anomalies`:
- **Voltage Spread**: `max_cell_v - min_cell_v`.
  - `>= 0.05V`: Minor
  - `>= 0.10V`: Major
- **Temperature**:
  - `>= 45°C`: Warning
  - `>= 60°C`: Critical
- **Pack Voltage Mismatch**: Implied cell voltage (`pack_voltage / cell_count`) outside the `2.5V - 4.5V` range is a warning.

### Report Structure
The final JSON report must be deterministic. The root keys are `vehicle_id`, `generated_at`, `soh`, `cycles`, `anomalies`, and `explanation`. The `soh` object must always include `soh_percent`, `method`, and `confidence`.

## 4. Key Files

- `battery_report.py`: The heart of the application. All core logic lives here.
- `tests/test_battery_report.py`: Canonical examples of how the core functions should behave.
- `sample_log.json`: The reference for input data structure.
- `README.md`: Contains user-facing documentation and setup instructions.
