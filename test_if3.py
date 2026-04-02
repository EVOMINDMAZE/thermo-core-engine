import pandas as pd
from thermoneural.data.synthetic import generate_sensor_data
from thermoneural.models.anomaly import AnomalyDetector
import copy
import numpy as np

print("Generating data...")
df = generate_sensor_data(days=30, n_assets=2)
detector = AnomalyDetector()

for asset in df['asset_id'].unique():
    print(f"Running for {asset}...")
    asset_df = df[df['asset_id'] == asset].copy()
    detector.fit_predict(asset_df, features=['temperature', 'pressure', 'vibration', 'current'])
    print(f"Done for {asset}")
