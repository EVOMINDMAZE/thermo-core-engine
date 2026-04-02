import pandas as pd

from thermoneural.models.anomaly import group_anomalies_into_incidents

df = pd.DataFrame({
    'timestamp': pd.date_range('2023-01-01', periods=10, freq='h'),
    'is_anomaly': [False, True, True, False, False, True, False, True, True, True]
})

incidents = group_anomalies_into_incidents(df)
print(incidents)
