from thermoneural.data.synthetic import generate_sensor_data


def test_generate_sensor_data_default():
    df = generate_sensor_data()

    # 30 days * 24 hours = 720 rows
    assert len(df) == 720
    assert list(df.columns) == ['timestamp', 'temperature', 'pressure', 'vibration', 'current', 'is_anomaly', 'asset_id']

    # Check if there are anomalies
    assert df['is_anomaly'].sum() == 5
    assert df['asset_id'].iloc[0] == 'Asset-1'

def test_generate_sensor_data_custom_days():
    df = generate_sensor_data(days=10)

    # 10 days * 24 hours = 240 rows
    assert len(df) == 240

    # Check anomaly presence
    assert df['is_anomaly'].sum() == 5
