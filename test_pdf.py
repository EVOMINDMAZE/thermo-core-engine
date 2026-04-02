import pandas as pd
from thermoneural.reports.generator import generate_pdf_report

df = pd.DataFrame({'timestamp': pd.date_range('2023-01-01', periods=10), 'temperature': [1]*10, 'vibration': [1]*10, 'is_anomaly': [False]*10})
analysis = {"failure_mode": "Test", "confidence": 100, "confidence_std": 5, "severity": "High", "downtime_risk": "Low", "likely_root_cause": "Test", "actions": "Test"}
generate_pdf_report(df, analysis, "test.pdf")
print("PDF Generated!")
