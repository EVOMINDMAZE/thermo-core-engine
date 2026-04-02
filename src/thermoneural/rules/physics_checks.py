import pandas as pd


def calculate_physics_residuals(df: pd.DataFrame) -> pd.Series:
    """
    Checks a basic thermodynamic relationship (e.g., Temperature-Pressure proportionality).
    Returns a physics_residual column representing the deviation from the expected relationship.
    """
    if 'temperature' in df.columns and 'pressure' in df.columns:
        # Assuming temperature is in Celsius, convert to Kelvin for a basic proportionality check
        temp_k = df['temperature'] + 273.15
        pressure = df['pressure']

        # Estimate the constant of proportionality (k = P / T)
        mean_p = pressure.mean()
        mean_t = temp_k.mean()

        if mean_t != 0:
            k = mean_p / mean_t
            # Calculate the residual: actual pressure - expected pressure
            residual = pressure - (k * temp_k)
            residual.name = "physics_residual"
            return residual.fillna(0)

    # Fallback if columns are missing or if calculation fails
    return pd.Series(0.0, index=df.index, name="physics_residual")
