# Tasks
- [x] Task 1: Physics-Informed Rules (Domain Integration)
  - [x] SubTask 1.1: Create `src/thermoneural/rules/physics_checks.py`. Implement a function `calculate_physics_residuals(df)` that checks a basic thermodynamic relationship (e.g., Temperature-Pressure proportionality) and returns a `physics_residual` column.
  - [x] SubTask 1.2: Update `AnomalyDetector.fit_predict` in `anomaly.py` to append the `physics_residual` to the feature set `X` before passing it to the Isolation Forest.
  - [x] SubTask 1.3: Update `test_anomaly.py` to ensure the residual is correctly calculated and doesn't break the pipeline.
- [x] Task 2: Uncertainty Quantification
  - [x] SubTask 2.1: Update `AnomalyDetector` to use bootstrapping or conformal prediction. E.g., fit an `IsolationForest` ensemble or calculate standard deviation of decision function scores across bootstrapped samples to return an `anomaly_score_std` column.
  - [x] SubTask 2.2: Update the UI in `app.py`'s Top Summary Block to display the confidence as "85% ± 5%".
- [x] Task 3: Audit Log & Prediction History
  - [x] SubTask 3.1: Create `src/thermoneural/storage/db.py` using `sqlite3`. Initialize a `runs` table (id, timestamp, asset_id, failure_mode, confidence, total_risk).
  - [x] SubTask 3.2: Add a `save_run(analysis_dict)` function that inserts the result into the database.
  - [x] SubTask 3.3: Call `save_run()` inside `app.py` after `analyze_root_cause()`.
- [x] Task 4: Multi-Asset / Fleet View
  - [x] SubTask 4.1: Update `generate_sensor_data(num_assets=3)` in `synthetic.py` to generate an `asset_id` column.
  - [x] SubTask 4.2: Update `validation.py` to ensure `asset_id` is parsed or defaults to "Asset-1".
  - [x] SubTask 4.3: Refactor `app.py` to group by `asset_id`. If multiple assets exist, add a "Fleet Overview" tab that displays a sorted table of assets by `total_risk`.
  - [x] SubTask 4.4: Allow users to click/select a specific asset from the Fleet Overview to dive into the existing "Executive Summary" and "Technical Diagnostics" tabs.

# Task Dependencies
- Task 4 depends on updates to the synthetic generator to produce multiple assets.
- Task 1, 2, and 3 can be executed independently.