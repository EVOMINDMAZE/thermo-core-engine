import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from thermoneural.rules.expert_system import analyze_root_cause


def test_analyze_root_cause_scroll_valve_leak():
    # Simulate an anomaly with peak values that trigger the leak rule
    data = {
        'temperature': [20.0, 22.5, 35.0, 21.0],
        'vibration': [0.5, 0.6, 2.5, 0.4]
    }
    df = pd.DataFrame(data)

    result = analyze_root_cause(df)

    assert result['failure_mode'] == 'Scroll Valve Leak'
    assert result['confidence'] == 85.0
    assert result['etf'] == '7-14 days'
    assert 'Inspect scroll valve seals' in result['actions']
    assert result['peak_temp'] == '35.0 °C'
    assert result['peak_vib'] == '2.50 mm/s'
    assert result['peak_pressure'] == 'N/A'
    assert result['peak_current'] == 'N/A'
    assert result['downtime_cost'] == '$50,000'
    assert result['repair_cost'] == '$10,000'
    assert result['total_risk'] == '$60,000'

def test_analyze_root_cause_generic_anomaly():
    # Simulate an anomaly that doesn't meet the threshold
    data = {
        'temperature': [20.0, 22.5, 25.0, 21.0],
        'vibration': [0.5, 0.6, 0.8, 0.4]
    }
    df = pd.DataFrame(data)

    result = analyze_root_cause(df)

    assert result['failure_mode'] == 'Generic Anomaly'
    assert result['confidence'] == 50.0
    assert result['etf'] == 'Unknown'
    assert result['peak_temp'] == '25.0 °C'
    assert result['peak_vib'] == '0.80 mm/s'
    assert result['peak_pressure'] == 'N/A'
    assert result['peak_current'] == 'N/A'
    assert result['total_risk'] == 'High Risk'

def test_analyze_root_cause_empty():
    # Test with empty dataframe
    df = pd.DataFrame()
    result = analyze_root_cause(df)

    assert result['failure_mode'] == 'Unknown'
    assert result['confidence'] == 0.0
    assert result['severity'] == 'Normal'
    assert result['likely_root_cause'] == 'N/A'
    assert result['downtime_risk'] == 'None'
    assert result['etf'] == 'N/A'
    assert result['peak_temp'] == 'N/A'
    assert result['peak_vib'] == 'N/A'
    assert result['peak_pressure'] == 'N/A'
    assert result['peak_current'] == 'N/A'
    assert result['total_risk'] == '$0'

def test_analyze_root_cause_refrigerant_leak():
    # Simulate an anomaly with drop in pressure and temperature
    data = {
        'temperature': [20.0, 22.5, 8.0, 21.0],
        'pressure': [100.0, 98.0, 85.0, 99.0],
        'vibration': [0.5, 0.6, 0.5, 0.4]
    }
    df = pd.DataFrame(data)

    result = analyze_root_cause(df)

    assert result['failure_mode'] == 'Refrigerant Leak'
    assert result['confidence'] == 90.0
    assert result['peak_temp'] == '22.5 °C'  # max is 22.5, wait, the max temp is 22.5 but it triggered because min < 10
    # Actually, peak_temp is formatted as max_temp. So 22.5
    assert result['peak_pressure'] == '85.0 kPa'  # 100-85 (15) > 100-100 (0)
    assert result['peak_current'] == 'N/A'

def test_analyze_root_cause_motor_overload():
    # Simulate an anomaly with spike in temperature and current
    data = {
        'temperature': [20.0, 22.5, 35.0, 21.0],
        'current': [15.0, 16.0, 25.0, 15.5]
    }
    df = pd.DataFrame(data)

    result = analyze_root_cause(df)

    assert result['failure_mode'] == 'Motor Overload'
    assert result['confidence'] == 88.0
    assert result['peak_temp'] == '35.0 °C'
    assert result['peak_current'] == '25.0 A'

def test_analyze_root_cause_bearing_failure():
    # Simulate an anomaly with spike in vibration and current
    data = {
        'vibration': [0.5, 0.6, 2.0, 0.4],
        'current': [15.0, 16.0, 25.0, 15.5]
    }
    df = pd.DataFrame(data)

    result = analyze_root_cause(df)

    assert result['failure_mode'] == 'Bearing Failure'
    assert result['confidence'] == 92.0
    assert result['severity'] == 'High'
    assert result['likely_root_cause'] == 'Lack of lubrication or normal wear'
    assert result['downtime_risk'] == 'Medium'
    assert result['peak_vib'] == '2.00 mm/s'
    assert result['peak_current'] == '25.0 A'

def test_dynamic_rule_loading(tmp_path):
    import yaml

    from thermoneural.rules.expert_system import analyze_root_cause

    # Create a temporary rules file
    rules_data = {
        'rules': [
            {
                'name': 'Test Custom Rule',
                'conditions': [
                    {'feature': 'temperature', 'agg': 'max', 'operator': '>', 'value': 50}
                ],
                'confidence': 150.0,
                'etf': '0 days',
                'actions': 'Test action',
                'downtime_cost': '$0',
                'repair_cost': '$0',
                'total_risk': '$0'
            }
        ]
    }

    rules_file = tmp_path / "test_rules.yaml"
    with open(rules_file, 'w') as f:
        yaml.dump(rules_data, f)

    data = {
        'temperature': [20.0, 60.0, 25.0]
    }
    df = pd.DataFrame(data)

    # Analyze with the temporary rules file
    result = analyze_root_cause(df, rules_filepath=str(rules_file))

    assert result['failure_mode'] == 'Test Custom Rule'
    assert result['confidence'] == 100.0
    assert result['severity'] == 'Unknown'
    assert result['likely_root_cause'] == 'Unknown'
    assert result['downtime_risk'] == 'Unknown'
