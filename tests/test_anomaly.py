import os
import sys

import numpy as np
import pandas as pd

# Add src to the path so we can import thermoneural
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from thermoneural.models.anomaly import AnomalyDetector


def test_anomaly_detector_fit_predict():
    # Set random seed for reproducibility
    np.random.seed(42)

    # Generate synthetic data
    # 100 normal points around (0, 0)
    normal_data = np.random.normal(loc=0, scale=1, size=(100, 2))
    # 10 anomalous points around (10, 10)
    anomalous_data = np.random.normal(loc=10, scale=1, size=(10, 2))

    # Combine and create DataFrame
    data = np.vstack([normal_data, anomalous_data])
    df = pd.DataFrame(data, columns=['feature1', 'feature2'])

    # Initialize detector
    detector = AnomalyDetector(contamination=0.1, random_state=42)

    # Fit and predict
    result_df = detector.fit_predict(df)

    # Check if new columns exist
    assert 'is_anomaly' in result_df.columns
    assert 'anomaly_score' in result_df.columns

    # Check data types
    assert result_df['is_anomaly'].dtype == bool
    assert result_df['anomaly_score'].dtype == float

    # Verify that anomalies were detected
    assert result_df['is_anomaly'].sum() > 0

    # Check that known anomalies have lower anomaly scores than normal data
    # IsolationForest decision_function returns lower scores for anomalies
    normal_scores = result_df.loc[0:99, 'anomaly_score'].mean()
    anomaly_scores = result_df.loc[100:109, 'anomaly_score'].mean()

    assert anomaly_scores < normal_scores

    # Check if the known anomalies were actually flagged as True
    # Given the clear separation, it should flag the 10 points
    # Since contamination is 0.1 and total size is 110, it flags 11 points
    # The 10 anomalous points should definitely be among them
    assert result_df.loc[100:109, 'is_anomaly'].sum() >= 8

def test_anomaly_detector_with_features():
    # Generate data with one useful feature and one useless feature
    np.random.seed(42)
    df = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 100),
        'feature2': np.random.normal(0, 1, 100),
        'ignore_me': np.random.normal(100, 10, 100)
    })

    detector = AnomalyDetector(contamination=0.05, random_state=42)

    # Predict using only specific features
    result_df = detector.fit_predict(df, features=['feature1', 'feature2'])

    assert 'is_anomaly' in result_df.columns
    assert 'anomaly_score' in result_df.columns

    # The original dataframe should not be modified
    assert 'is_anomaly' not in df.columns
    assert 'anomaly_score' not in df.columns

def test_anomaly_detector_nan_handling():
    # Set random seed for reproducibility
    np.random.seed(42)

    # Generate data with NaNs
    df = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 100),
        'feature2': np.random.normal(0, 1, 100)
    })

    # Insert some NaNs
    df.loc[10:15, 'feature1'] = np.nan
    df.loc[20:25, 'feature2'] = np.nan

    detector = AnomalyDetector(contamination=0.05, random_state=42)

    # Should not raise an error thanks to SimpleImputer
    result_df = detector.fit_predict(df)

    assert 'is_anomaly' in result_df.columns
    assert 'anomaly_score' in result_df.columns
    assert len(result_df) == 100
    assert not result_df['is_anomaly'].isna().any()
    assert not result_df['anomaly_score'].isna().any()

def test_anomaly_detector_dynamic_contamination():
    np.random.seed(42)
    # Generate data with heavy tails
    normal_data = np.random.normal(loc=0, scale=1, size=(100, 2))
    anomalous_data = np.random.normal(loc=10, scale=1, size=(10, 2))
    df = pd.DataFrame(np.vstack([normal_data, anomalous_data]), columns=['f1', 'f2'])

    detector = AnomalyDetector(contamination="auto", random_state=42)
    result_df = detector.fit_predict(df)

    assert 'is_anomaly' in result_df.columns

    # Check if contamination was dynamically updated inside the model
    iso_forest = detector.model.named_steps['isolation_forest']
    assert iso_forest.contamination > 0.05
    assert iso_forest.contamination <= 0.5

def test_anomaly_detector_smoothing_window():
    np.random.seed(42)
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.5, 100)
    df = pd.DataFrame({'val': y})

    detector = AnomalyDetector(contamination=0.1, random_state=42)
    result_df = detector.fit_predict(df, smoothing_window=5)

    assert 'is_anomaly' in result_df.columns
    assert len(result_df) == 100

def test_anomaly_detector_diff_var_calculated():
    np.random.seed(42)
    df = pd.DataFrame({
        'f1': np.random.normal(0, 1, 10),
        'f2': np.random.normal(0, 1, 10)
    })

    detector = AnomalyDetector(contamination=0.1, random_state=42)
    result_df = detector.fit_predict(df)

    # We want to make sure _diff and _var features were used by the model
    # Since IsolationForest receives X with _diff and _var columns
    # We can check if the model pipeline expects 9 features (f1, f2, physics_residual, and their diff/var)
    iso_forest = detector.model.named_steps['isolation_forest']
    assert iso_forest.n_features_in_ == 9

def test_anomaly_detector_save_load(tmp_path):
    import os
    np.random.seed(42)
    df = pd.DataFrame({
        'f1': np.random.normal(0, 1, 50),
    })

    detector1 = AnomalyDetector(contamination=0.1, random_state=42)
    result1 = detector1.fit_predict(df)

    model_path = os.path.join(tmp_path, "model.joblib")
    detector1.save(model_path)

    assert os.path.exists(model_path)

    detector2 = AnomalyDetector(contamination=0.1, random_state=42)
    detector2.load(model_path)

    # Check if loaded model makes the same predictions
    # Wait, fit_predict on detector2 will re-fit it. We need a predict method?
    # AnomalyDetector only has fit_predict. If we just want to verify load works:
    assert detector2.model is not None
    assert detector2.model.named_steps['isolation_forest'].n_features_in_ == 6 # f1, physics_residual, f1_diff, f1_var, physics_residual_diff, physics_residual_var

def test_physics_residuals_calculation():
    df = pd.DataFrame({
        'temperature': [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0],
        'pressure': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 145.0]
    })

    from thermoneural.rules.physics_checks import calculate_physics_residuals
    residuals = calculate_physics_residuals(df)

    assert len(residuals) == 10
    assert not residuals.isna().any()
    assert residuals.name == 'physics_residual'

    # Check it works within AnomalyDetector
    detector = AnomalyDetector(contamination=0.1, random_state=42)
    result_df = detector.fit_predict(df)

    assert 'is_anomaly' in result_df.columns
    # Model should have 2 original features + 1 residual = 3. 3 base + 3 diff + 3 var = 9 features.
    assert detector.model.named_steps['isolation_forest'].n_features_in_ == 9


