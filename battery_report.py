"""
EV Battery Health Report Generator

This script processes EV diagnostic JSON logs to generate a comprehensive battery health 
report. It calculates the State of Health (SOH), counts charge/discharge cycles, and 
detects anomalies like voltage imbalance and overheating.

Usage:
    python battery_report.py [path_to_log.json]

Example:
    python battery_report.py sample_log.json
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def compute_soh(raw: dict) -> dict:
    """
    Computes the battery's State of Health (SOH) using one of three methods.

    Args:
        raw (dict): The raw JSON log data.

    Returns:
        dict: A dictionary containing the SOH percentage, method, and confidence level.
    """
    if 'measured_capacity_kwh' in raw and 'nominal_capacity_kwh' in raw:
        soh_percent = (raw['measured_capacity_kwh'] / raw['nominal_capacity_kwh']) * 100
        return {"soh_percent": round(soh_percent, 2), "method": "measured_capacity", "confidence": "high"}
    
    if 'cycle_history' in raw and raw['cycle_history']:
        total_energy = sum(c['energy_kwh'] for c in raw['cycle_history'])
        avg_energy = total_energy / len(raw['cycle_history'])
        soh_percent = (avg_energy / raw['nominal_capacity_kwh']) * 100
        return {"soh_percent": round(soh_percent, 2), "method": "cycle_history_estimate", "confidence": "medium"}

    # Fallback to voltage heuristic
    if 'cells' in raw and raw['cells']:
        avg_voltage = sum(c['voltage'] for c in raw['cells']) / len(raw['cells'])
        soh_percent = 30 + (avg_voltage - 3.2) / (4.2 - 3.2) * 70
        return {"soh_percent": round(soh_percent, 2), "method": "voltage_heuristic", "confidence": "low"}

    return {"soh_percent": 0, "method": "unknown", "confidence": "none"}


def count_cycles_from_soc(soc_series: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Counts equivalent full cycles and deep discharge cycles from an SoC time-series.

    Args:
        soc_series (List[Dict[str, Any]]): A list of SoC readings with timestamps.

    Returns:
        Dict[str, Any]: A dictionary with the counts of equivalent and deep cycles.
    """
    if not soc_series or len(soc_series) < 2:
        return {"equivalent_full_cycles": 0, "deep_cycles": 0}

    total_delta_soc = sum(abs(soc_series[i]['soc'] - soc_series[i-1]['soc']) for i in range(1, len(soc_series)))
    equivalent_full_cycles = total_delta_soc / 100

    deep_cycles = 0
    for i in range(1, len(soc_series)):
        if soc_series[i-1]['soc'] >= 90 and soc_series[i]['soc'] <= 20:
            deep_cycles += 1
            
    return {"equivalent_full_cycles": round(equivalent_full_cycles, 2), "deep_cycles": deep_cycles}


def detect_anomalies(raw: dict) -> List[Dict[str, Any]]:
    """
    Detects anomalies such as voltage imbalance and overheating.

    Args:
        raw (dict): The raw JSON log data.

    Returns:
        List[Dict[str, Any]]: A list of detected anomalies.
    """
    anomalies = []
    if 'cells' in raw and raw['cells']:
        voltages = [c['voltage'] for c in raw['cells']]
        temps = [c['temp_c'] for c in raw['cells']]
        
        voltage_spread = max(voltages) - min(voltages)
        if voltage_spread >= 0.10:
            anomalies.append({"type": "voltage_imbalance", "severity": "major", "value": round(voltage_spread, 3)})
        elif voltage_spread >= 0.05:
            anomalies.append({"type": "voltage_imbalance", "severity": "minor", "value": round(voltage_spread, 3)})

        if max(temps) >= 60:
            anomalies.append({"type": "overheating", "severity": "critical", "value": max(temps)})
        elif max(temps) >= 45:
            anomalies.append({"type": "overheating", "severity": "warning", "value": max(temps)})

    if 'pack_voltage' in raw and 'cell_count' in raw and raw['cell_count'] > 0:
        implied_cell_v = raw['pack_voltage'] / raw['cell_count']
        if not (2.5 <= implied_cell_v <= 4.5):
            anomalies.append({"type": "pack_voltage_mismatch", "severity": "warning", "value": round(implied_cell_v, 2)})
            
    return anomalies


def generate_report(raw: dict) -> dict:
    """
    Generates the full battery health report.

    Args:
        raw (dict): The raw JSON log data.

    Returns:
        dict: The complete battery health report.
    """
    soh = compute_soh(raw)
    cycles = count_cycles_from_soc(raw.get('soc_timeseries', []))
    anomalies = detect_anomalies(raw)
    
    explanation = f"Battery SOH is {soh['soh_percent']}% (calculated via {soh['method']}). "
    explanation += f"Total equivalent cycles: {cycles['equivalent_full_cycles']}. "
    explanation += f"Detected {len(anomalies)} anomalies."

    return {
        "vehicle_id": raw.get("vehicle_id", "Unknown"),
        "generated_at": datetime.utcnow().isoformat(),
        "soh": soh,
        "cycles": cycles,
        "anomalies": anomalies,
        "explanation": explanation
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a battery health report from EV diagnostic logs.")
    parser.add_argument("filepath", type=str, nargs='?', default="sample_log.json",
                        help="Path to the JSON log file (default: sample_log.json)")
    args = parser.parse_args()

    try:
        with open(args.filepath, 'r') as f:
            log_data = json.load(f)
        
        report = generate_report(log_data)
        
        # Print human-readable report
        print("--- Battery Health Report ---")
        print(f"Vehicle ID: {report['vehicle_id']}")
        print(f"Generated At: {report['generated_at']}")
        print(f"\nState of Health (SOH): {report['soh']['soh_percent']}%")
        print(f"  - Method: {report['soh']['method']}")
        print(f"  - Confidence: {report['soh']['confidence']}")
        print(f"\nCycles:")
        print(f"  - Equivalent Full Cycles: {report['cycles']['equivalent_full_cycles']}")
        print(f"  - Deep Discharge Cycles: {report['cycles']['deep_cycles']}")
        print(f"\nAnomalies ({len(report['anomalies'])}):")
        if report['anomalies']:
            for anomaly in report['anomalies']:
                print(f"  - Type: {anomaly['type']}, Severity: {anomaly['severity']}, Value: {anomaly['value']}")
        else:
            print("  - None detected.")
        
        # Write machine-readable report
        output_filepath = "battery_report_output.json"
        with open(output_filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info(f"Successfully generated report. Output saved to {output_filepath}")

    except FileNotFoundError:
        logging.error(f"Error: The file '{args.filepath}' was not found.")
    except json.JSONDecodeError:
        logging.error(f"Error: Could not decode JSON from the file '{args.filepath}'.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
