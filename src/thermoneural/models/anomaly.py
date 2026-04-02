import copy

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from thermoneural.utils.logger import get_logger

logger = get_logger(__name__)


class AnomalyDetector:
    def __init__(self, contamination="auto", random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        logger.info(f"Initializing AnomalyDetector with contamination={self.contamination}, random_state={self.random_state}")
        self.model = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('isolation_forest', IsolationForest(
                contamination=self.contamination,
                random_state=self.random_state
            ))
        ])

    def fit_predict(self, df: pd.DataFrame, features: list[str] = None, smoothing_window: int = None) -> pd.DataFrame:
        """
        Fits the IsolationForest model and predicts anomalies.

        Args:
            df: Input pandas DataFrame.
            features: List of column names to use for anomaly detection.
                      If None, all columns are used.
            smoothing_window: Optional window size for applying a rolling mean.

        Returns:
            A new DataFrame with 'is_anomaly' and 'anomaly_score' columns added.
        """
        logger.info(f"Starting fit_predict on dataset of shape {df.shape}")
        result_df = df.copy()

        if features is None:
            logger.info("No specific features provided. Using all columns.")
            X = df.copy()
        else:
            logger.info(f"Using specified features: {features}")
            X = df[features].copy()

        # Append physics residual
        from thermoneural.rules.physics_checks import calculate_physics_residuals
        X['physics_residual'] = calculate_physics_residuals(df)

        # Calculate _diff and _var for numeric columns
        numeric_cols = X.select_dtypes(include='number').columns
        for col in numeric_cols:
            X[f"{col}_diff"] = X[col].diff().fillna(0)
            X[f"{col}_var"] = X[col].rolling(window=5, min_periods=1).var().fillna(0)

        if smoothing_window is not None and smoothing_window > 1:
            logger.info(f"Applying rolling mean with window={smoothing_window}")
            X_numeric = X.select_dtypes(include='number')
            X[X_numeric.columns] = X_numeric.rolling(window=smoothing_window, min_periods=1).mean()

        if self.contamination == "auto":
            # Calculate kurtosis ONLY on the raw features, not the derived ones
            # Derived features like diff and var are highly spiky and will artificially inflate kurtosis
            numeric_X = X[features].select_dtypes(include='number') if features else df.select_dtypes(include='number')
            
            if not numeric_X.empty:
                mean_variance = numeric_X.var(skipna=True).mean()
                mean_kurtosis = numeric_X.kurtosis(skipna=True).mean()

                if pd.isna(mean_kurtosis):
                    dynamic_contam = 0.05
                else:
                    # Invert the relationship: Higher kurtosis means outliers are more extreme/easier to separate,
                    # so we need a LOWER contamination rate. 
                    # Also cap the absolute maximum contamination at 0.15 (15%) instead of 0.5 (50%)
                    # Base is 0.10. For every unit of kurtosis, we subtract a small amount.
                    calculated = 0.10 - (0.001 * mean_kurtosis)
                    dynamic_contam = min(0.15, max(0.01, calculated))

                logger.info(f"Dynamically calculated contamination: {dynamic_contam:.4f} "
                            f"(variance={mean_variance:.2f}, kurtosis={mean_kurtosis:.2f})")
                self.model.named_steps['isolation_forest'].set_params(contamination=dynamic_contam)

        # Fit and predict (-1 for anomalies, 1 for normal)
        logger.debug("Fitting model and predicting anomalies...")
        predictions = self.model.fit_predict(X)

        # Calculate anomaly scores (lower is more anomalous)
        logger.debug("Calculating anomaly scores...")
        scores = self.model.decision_function(X)

        # Calculate bootstrapped standard deviation of the anomaly scores
        logger.debug("Calculating bootstrapped anomaly score std...")

        iso_forest = self.model.named_steps['isolation_forest']
        n_estimators = len(iso_forest.estimators_)
        n_bootstraps = 50

        # Transform X through the pipeline up to the isolation_forest
        X_transformed = X
        for name, step in self.model.steps[:-1]:
            if step is not None and step != 'passthrough':
                X_transformed = step.transform(X_transformed)

        rng = np.random.default_rng(self.random_state if isinstance(self.random_state, int) else 42)
        
        # Safe extraction of individual tree scores (depths)
        tree_depths = []
        estimators_features = getattr(iso_forest, '_estimators_features', iso_forest.estimators_features_)
        for tree, features in zip(iso_forest.estimators_, estimators_features):
            leaves_index = tree.apply(X_transformed[:, features])
            node_depths = tree.tree_.compute_node_depths()
            
            # Scikit-learn adds an adjustment for leaf size
            # We will just use the raw node depth as an approximation for the score variance
            tree_depths.append(node_depths[leaves_index])
            
        tree_depths = np.array(tree_depths) # shape: (n_estimators, n_samples)
        
        boot_scores = []
        for _ in range(n_bootstraps):
            indices = rng.choice(n_estimators, size=n_estimators, replace=True)
            # average depth for these selected trees
            avg_depth = tree_depths[indices].mean(axis=0)
            
            # Anomaly score is monotonically related to average depth.
            # We'll just compute score = 2 ** (-avg_depth / c)
            # where c is average path length. 
            # We can approximate c by just using a constant or the average of avg_depths over all samples
            # Or we can just use the score_samples formula from sklearn if we can
            
            # The actual formula is: 2 ** (-avg_depth / c)
            # We can use the global average depth as an approximation for c, or just return the variance of depths.
            # But since we just want the std of the scores, and score = 2 ** (-depth / c):
            # For simplicity and robustness, let's just evaluate it as:
            c = np.mean(tree_depths) # rough approximation for c
            if c == 0: c = 1
            boot_scores.append(- (2 ** (-avg_depth / c)))

        boot_scores = np.array(boot_scores)
        score_std = np.std(boot_scores, axis=0)

        # Add columns: 'is_anomaly' as boolean, 'anomaly_score' as float
        result_df['is_anomaly'] = predictions == -1
        result_df['anomaly_score'] = scores
        result_df['anomaly_score_std'] = score_std

        num_anomalies = result_df['is_anomaly'].sum()
        logger.info(f"Anomaly detection complete. Found {num_anomalies} anomalies.")

        return result_df

    def save(self, filepath: str):
        """Saves the fitted model pipeline to a file using joblib."""
        logger.info(f"Saving model to {filepath}")
        joblib.dump(self.model, filepath)

    def load(self, filepath: str):
        """Loads a model pipeline from a file using joblib."""
        logger.info(f"Loading model from {filepath}")
        self.model = joblib.load(filepath)

def group_anomalies_into_incidents(df: pd.DataFrame, time_gap: pd.Timedelta = pd.Timedelta(hours=2)) -> list:
    """
    Groups individual anomalies into discrete incidents based on a time gap.
    
    Args:
        df: DataFrame containing 'timestamp' and 'is_anomaly' columns.
        time_gap: Maximum time gap between anomalies to be considered part of the same incident.
        
    Returns:
        List of DataFrames, each representing an incident.
    """
    if 'timestamp' not in df.columns or 'is_anomaly' not in df.columns:
        logger.warning("DataFrame missing 'timestamp' or 'is_anomaly' columns. Cannot group incidents.")
        return []

    anomalies = df[df['is_anomaly']].copy()
    if anomalies.empty:
        return []

    # Ensure sorted by timestamp
    anomalies = anomalies.sort_values('timestamp')

    # Calculate time difference between consecutive anomalies
    time_diff = anomalies['timestamp'].diff()

    # Identify incident boundaries (where time gap > time_gap)
    # The first row will have NaT, so it evaluates to False (not a new incident gap)
    is_new_incident = time_diff > time_gap

    # Create incident IDs using cumulative sum of new incident flags
    anomalies['incident_id'] = is_new_incident.cumsum()

    incidents = []
    for _, group in anomalies.groupby('incident_id'):
        incident_df = group.drop(columns=['incident_id'])
        incidents.append(incident_df)

    return incidents
