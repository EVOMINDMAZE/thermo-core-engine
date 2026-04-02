import numpy as np
import pandas as pd


def generate_sensor_data(days=30, n_assets=1):
    """
    Generate synthetic sensor data with a sine wave, noise, and a localized anomaly.

    Args:
        days (int): Number of days of data to generate (1 data point per hour).
        n_assets (int): Number of distinct assets to generate data for.

    Returns:
        pd.DataFrame: DataFrame containing timestamp, temperature, pressure, vibration, current, is_anomaly, and asset_id.
    """
    dfs = []
    for asset_idx in range(1, n_assets + 1):
        hours = days * 24

        # Generate timestamps
        timestamps = pd.date_range(start="2026-01-01", periods=hours, freq="h")

        # Generate base sine wave (daily cycle: period = 24 hours)
        t = np.arange(hours)

        # Temperature: 20 +/- 10
        temperature_base = 20 + 10 * np.sin(2 * np.pi * t / 24)
        temperature = temperature_base + np.random.normal(0, 1.5, hours)

        # Pressure: 100 +/- 5
        pressure_base = 100 + 5 * np.cos(2 * np.pi * t / 24)
        pressure = pressure_base + np.random.normal(0, 0.5, hours)

        # Vibration: 0.5 +/- 0.1
        vibration = 0.5 + np.random.normal(0, 0.05, hours)

        # Current: 15 +/- 2
        current_base = 15 + 2 * np.sin(2 * np.pi * t / 24 + np.pi/4)
        current = current_base + np.random.normal(0, 0.2, hours)

        # Inject localized anomaly (at the middle)
        is_anomaly = np.zeros(hours, dtype=bool)

        mid_point = hours // 2
        anomaly_length = 5

        # Make sure we don't go out of bounds
        if mid_point + anomaly_length <= hours:
            # Shift the anomaly slightly per asset so they don't all happen exactly at the same hour
            mid_point = min(hours - anomaly_length, mid_point + (asset_idx - 1) * 24)
            
            # Cycle through different failure modes based on asset index to demonstrate fleet variety
            failure_type = asset_idx % 5
            
            if failure_type == 1:
                # Scroll Valve Leak: Temp > 30, Vib > 1.5
                temperature[mid_point:mid_point + anomaly_length] += 15 
                vibration[mid_point:mid_point + anomaly_length] += 2.0  
                is_anomaly[mid_point:mid_point + anomaly_length] = True
            elif failure_type == 2:
                # Motor Overload: Temp > 30, Current > 20
                temperature[mid_point:mid_point + anomaly_length] += 15
                current[mid_point:mid_point + anomaly_length] += 8.0
                is_anomaly[mid_point:mid_point + anomaly_length] = True
            elif failure_type == 3:
                # Refrigerant Leak: Pressure < 90, Temp < 10
                pressure[mid_point:mid_point + anomaly_length] -= 20.0
                temperature[mid_point:mid_point + anomaly_length] -= 20.0
                is_anomaly[mid_point:mid_point + anomaly_length] = True
            elif failure_type == 4:
                # Bearing Failure: Vib > 1.5, Current > 20
                vibration[mid_point:mid_point + anomaly_length] += 2.0
                current[mid_point:mid_point + anomaly_length] += 8.0
                is_anomaly[mid_point:mid_point + anomaly_length] = True
            else:
                # Normal Operation: No anomaly injected (failure_type == 0)
                pass

        df = pd.DataFrame({
            'timestamp': timestamps,
            'temperature': temperature,
            'pressure': pressure,
            'vibration': vibration,
            'current': current,
            'is_anomaly': is_anomaly,
            'asset_id': f'Asset-{asset_idx}'
        })
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)
