import pandas as pd

from thermoneural.utils.logger import get_logger

logger = get_logger(__name__)


def validate_sensor_data(df: pd.DataFrame) -> tuple[bool, str, pd.DataFrame]:
    """
    Validates sensor data DataFrame.
    Checks for a time column (and parses to datetime), and checks for numeric sensors.
    """
    logger.info("Starting data validation.")
    if df is None or df.empty:
        error_msg = "The uploaded data is empty."
        logger.warning(f"Validation failed: {error_msg}")
        return False, error_msg, df

    # Check for time column
    time_cols = ['timestamp', 'time', 'date', 'datetime']
    found_time_col = None
    for col in time_cols:
        if col in df.columns:
            found_time_col = col
            break

    if not found_time_col:
        error_msg = "Missing time column. Expected one of: timestamp, time, date, datetime."
        logger.warning(f"Validation failed: {error_msg}")
        return False, error_msg, df

    # Parse to datetime
    try:
        df[found_time_col] = pd.to_datetime(df[found_time_col])
        logger.debug(f"Successfully parsed '{found_time_col}' column to datetime.")
    except Exception as e:
        error_msg = f"Failed to parse time column '{found_time_col}' to datetime: {str(e)}"
        logger.error(f"Validation error: {error_msg}")
        return False, error_msg, df

    # Rename to 'timestamp' for consistency with the rest of the app
    if found_time_col != 'timestamp':
        df = df.rename(columns={found_time_col: 'timestamp'})

    # Check for numeric sensors
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) == 0:
        error_msg = "No numeric sensor columns found."
        logger.warning(f"Validation failed: {error_msg}")
        return False, error_msg, df

    # Optionally check for specific sensors
    expected_sensors = ['temperature', 'pressure', 'vibration', 'current']
    found_sensors = [col for col in expected_sensors if col in df.columns]

    if len(found_sensors) == 0:
        error_msg = f"Missing expected sensor columns. Expected at least one of: {', '.join(expected_sensors)}."
        logger.warning(f"Validation failed: {error_msg}")
        return False, error_msg, df

    # Ensure asset_id exists
    if 'asset_id' not in df.columns:
        df['asset_id'] = 'Asset-1'
        logger.info("Added default 'asset_id' column with value 'Asset-1'.")

    logger.info(f"Data validation successful. Found sensors: {found_sensors}")
    return True, "", df
