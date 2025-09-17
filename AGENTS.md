# AGENT INSTRUCTIONS — EV Battery Health Report

You are an **AI coding assistant** working inside this repository.  
Your job is to help the developer (me) implement a **Python FastAPI backend** that processes EV diagnostic logs and generates battery health reports.

---

## 🎯 Project Goal
- Build a **battery health reporting service** in **Python 3.9+**.
- Input: mock JSON logs of EV battery data.
- Output: JSON report containing:
  - **State of Health (SOH)** in %
  - **Charge/discharge cycle count**
  - **Anomalies** (voltage imbalance, overheating, pack mismatch)

---

## 📂 Expected Files
- `battery_report.py` → Core logic (functions for SOH, cycles, anomalies, report generator).
- `api.py` → FastAPI app exposing:
  - `POST /v1/battery_report` → takes JSON input, returns generated report.
- `sample_log.json` → Mock example input.
- `battery_report_output.json` → Example output.
- `tests/test_battery_report.py` → pytest unit tests.
- `README.md` → Setup, usage, production notes.
- `.gitignore`

---

## 🧮 Algorithms & Thresholds
- **SOH**
  - If `measured_capacity_kwh` & `nominal_capacity_kwh`: `SOH% = measured / nominal * 100`.
  - Else fallback: average cell voltage mapped linearly → 3.2V = 30%, 4.2V = 100%.
- **Cycles**
  - Equivalent cycles = `sum(abs(delta_soc)) / 100`.
  - Deep cycles = count where SoC drops from ≥90% to ≤20%.
- **Anomalies**
  - Voltage spread: warn ≥0.05V, critical ≥0.10V.
  - Temperature: warn ≥45°C, critical ≥60°C.
  - Pack voltage mismatch: implied cell voltage <2.5V or >4.5V.

---

## 📝 Coding Conventions
- Use **FastAPI** with **Pydantic** models for input/output validation.
- Return JSON with keys:
  ```json
  {
    "vehicle_id": "...",
    "generated_at": "...",
    "soh": { "percent": 71.0, "method": "measured_capacity" },
    "cycles": { "equivalent_full_cycles": 350, "deep_cycles": 12 },
    "anomalies": [],
    "explanation": "Battery health is within expected range for its age."
  }
