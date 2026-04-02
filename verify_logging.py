import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).parent / "src"))

from thermoneural.data.synthetic import generate_sensor_data
from thermoneural.data.validation import validate_sensor_data
from thermoneural.models.anomaly import AnomalyDetector
from thermoneural.rules.expert_system import analyze_root_cause
from thermoneural.utils.logger import get_logger

logger = get_logger("test_run")
logger.info("Test script started")

# Generate data
df = generate_sensor_data(days=2)
logger.info("Generated data")

# Validate data
is_valid, msg, df = validate_sensor_data(df)
logger.info(f"Validation: {is_valid}, {msg}")

# Anomaly detection
detector = AnomalyDetector()
features = ['temperature', 'pressure', 'vibration', 'current']
df_results = detector.fit_predict(df, features=features)
logger.info("Completed fit_predict")

# Expert system
anomalies = df_results[df_results['is_anomaly']]
analysis = analyze_root_cause(anomalies)
logger.info(f"Expert system returned: {analysis['failure_mode']}")

logger.info("Test script finished")
