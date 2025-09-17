import pytest
from battery_report import (
    compute_soh,
    count_cycles_from_soc,
    detect_anomalies,
    generate_report
)

@pytest.fixture
def sample_log_measured():
    return {
        "vehicle_id": "VIN-TEST-001",
        "nominal_capacity_kwh": 75.0,
        "measured_capacity_kwh": 53.25,
        "pack_voltage": 350.5,
        "cell_count": 96,
        "cells": [
            {"id": 1, "voltage": 3.65, "temp_c": 28},
            {"id": 96, "voltage": 3.75, "temp_c": 61}
        ],
        "soc_timeseries": [
            {"ts": "2025-09-16T12:00:00Z", "soc": 95},
            {"ts": "2025-09-16T14:00:00Z", "soc": 18}
        ]
    }

@pytest.fixture
def sample_log_cycle():
    return {
        "vehicle_id": "VIN-TEST-002",
        "nominal_capacity_kwh": 80.0,
        "pack_voltage": 360.0,
        "cell_count": 96,
        "cells": [{"id": 1, "voltage": 3.8, "temp_c": 30}],
        "cycle_history": [
            {"energy_kwh": 60.0},
            {"energy_kwh": 62.0}
        ]
    }

@pytest.fixture
def sample_log_voltage():
    return {
        "vehicle_id": "VIN-TEST-003",
        "nominal_capacity_kwh": 60.0,
        "pack_voltage": 340.0,
        "cell_count": 96,
        "cells": [
            {"id": 1, "voltage": 3.7, "temp_c": 25},
            {"id": 2, "voltage": 3.7, "temp_c": 25}
        ]
    }

def test_soh_from_measured_capacity(sample_log_measured):
    soh = compute_soh(sample_log_measured)
    assert soh["soh_percent"] == 71.0
    assert soh["method"] == "measured_capacity"
    assert soh["confidence"] == "high"

def test_soh_from_cycle_history(sample_log_cycle):
    soh = compute_soh(sample_log_cycle)
    assert soh["soh_percent"] == 76.25 # (61 / 80) * 100
    assert soh["method"] == "cycle_history_estimate"
    assert soh["confidence"] == "medium"

def test_soh_from_voltage_heuristic(sample_log_voltage):
    soh = compute_soh(sample_log_voltage)
    assert soh["soh_percent"] == 65.0 # 30 + (3.7 - 3.2) / 1.0 * 70
    assert soh["method"] == "voltage_heuristic"
    assert soh["confidence"] == "low"

def test_cycle_counting():
    soc_series = [
        {"soc": 95}, {"soc": 18}, # Deep cycle
        {"soc": 88}, {"soc": 25}
    ]
    cycles = count_cycles_from_soc(soc_series)
    assert cycles["equivalent_full_cycles"] == 1.4
    assert cycles["deep_cycles"] == 1

def test_anomaly_detection():
    log = {
        "cells": [
            {"voltage": 3.60, "temp_c": 30},
            {"voltage": 3.71, "temp_c": 46}, # Major voltage spread, warning temp
            {"voltage": 3.65, "temp_c": 62}  # Critical temp
        ],
        "pack_voltage": 200,
        "cell_count": 96 # Implied voltage mismatch
    }
    anomalies = detect_anomalies(log)
    assert len(anomalies) == 3
    assert any(a['type'] == 'voltage_imbalance' and a['severity'] == 'major' for a in anomalies)
    assert any(a['type'] == 'overheating' and a['severity'] == 'critical' for a in anomalies)
    assert any(a['type'] == 'pack_voltage_mismatch' for a in anomalies)
