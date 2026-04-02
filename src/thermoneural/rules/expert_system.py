import os

import pandas as pd
import yaml

from thermoneural.utils.logger import get_logger

logger = get_logger(__name__)


def load_rules(filepath=None):
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), '..', 'config', 'rules.yaml')
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('rules', []) if data else []


def evaluate_condition(condition, df):
    feature = condition['feature']
    if feature not in df.columns:
        return False

    agg = condition['agg']
    operator = condition['operator']
    value = condition['value']

    if agg == 'min':
        agg_val = df[feature].min()
    elif agg == 'max':
        agg_val = df[feature].max()
    else:
        return False

    if operator == '>':
        return agg_val > value
    elif operator == '<':
        return agg_val < value
    elif operator == '>=':
        return agg_val >= value
    elif operator == '<=':
        return agg_val <= value
    elif operator == '==':
        return agg_val == value
    return False


def analyze_root_cause(anomalous_rows: pd.DataFrame, rules_filepath=None) -> dict:
    """
    Analyzes anomalous rows to determine the root cause of the failure dynamically using rules.yaml.
    """
    logger.info("Starting root cause analysis on anomalous rows.")
    if anomalous_rows is None or anomalous_rows.empty:
        logger.warning("No anomalous rows provided for root cause analysis.")
        return {
            "failure_mode": "Unknown",
            "confidence": 0.0,
            "severity": "Normal",
            "likely_root_cause": "N/A",
            "downtime_risk": "None",
            "etf": "N/A",
            "actions": "No anomalies detected.",
            "peak_temp": "N/A",
            "peak_vib": "N/A",
            "peak_pressure": "N/A",
            "peak_current": "N/A",
            "downtime_cost": "$0",
            "repair_cost": "$0",
            "total_risk": "$0"
        }

    # Extract peak values for reporting
    temp_max = anomalous_rows['temperature'].max() if 'temperature' in anomalous_rows.columns else 0
    vib_max = anomalous_rows['vibration'].max() if 'vibration' in anomalous_rows.columns else 0
    pressure_min = anomalous_rows['pressure'].min() if 'pressure' in anomalous_rows.columns else float('inf')
    pressure_max = anomalous_rows['pressure'].max() if 'pressure' in anomalous_rows.columns else 0
    current_max = anomalous_rows['current'].max() if 'current' in anomalous_rows.columns else 0

    peak_temp_str = f"{temp_max:.1f} °C" if temp_max > 0 else "N/A"
    peak_vib_str = f"{vib_max:.2f} mm/s" if vib_max > 0 else "N/A"

    # Determine the most extreme deviation for display
    if 'pressure' in anomalous_rows.columns:
        if (100 - pressure_min) > (pressure_max - 100):
            peak_pressure_str = f"{pressure_min:.1f} kPa"
        else:
            peak_pressure_str = f"{pressure_max:.1f} kPa"
    else:
        peak_pressure_str = "N/A"

    peak_current_str = f"{current_max:.1f} A" if current_max > 0 else "N/A"

    logger.debug(f"Calculated peak values: Temperature={peak_temp_str}, Vibration={peak_vib_str}, Pressure={peak_pressure_str}, Current={peak_current_str}")

    try:
        rules = load_rules(rules_filepath)
    except Exception as e:
        logger.error(f"Failed to load rules: {e}")
        rules = []

    for rule in rules:
        conditions_met = True
        for cond in rule.get('conditions', []):
            if not evaluate_condition(cond, anomalous_rows):
                conditions_met = False
                break

        if conditions_met:
            logger.info(f"Diagnosis: {rule['name']} detected.")

            try:
                confidence = float(rule.get('confidence', 0.0))
            except (ValueError, TypeError):
                confidence = 0.0
            confidence = max(0.0, min(100.0, confidence))

            return {
                "failure_mode": rule['name'],
                "confidence": confidence,
                "severity": rule.get('severity', 'Unknown'),
                "likely_root_cause": rule.get('likely_root_cause', 'Unknown'),
                "downtime_risk": rule.get('downtime_risk', 'Unknown'),
                "etf": rule.get('etf', 'Unknown'),
                "actions": rule.get('actions', ''),
                "peak_temp": peak_temp_str,
                "peak_vib": peak_vib_str,
                "peak_pressure": peak_pressure_str,
                "peak_current": peak_current_str,
                "downtime_cost": rule.get('downtime_cost', 'TBD'),
                "repair_cost": rule.get('repair_cost', 'TBD'),
                "total_risk": rule.get('total_risk', 'TBD')
            }

    logger.info("Diagnosis: Generic Anomaly detected. Could not match specific failure mode.")
    return {
        "failure_mode": "Generic Anomaly",
        "confidence": 50.0,
        "severity": "Unknown",
        "likely_root_cause": "Unknown",
        "downtime_risk": "Unknown",
        "etf": "Unknown",
        "actions": "Investigate system logs and inspect equipment.",
        "peak_temp": peak_temp_str,
        "peak_vib": peak_vib_str,
        "peak_pressure": peak_pressure_str,
        "peak_current": peak_current_str,
        "downtime_cost": "TBD",
        "repair_cost": "TBD",
        "total_risk": "High Risk"
    }
