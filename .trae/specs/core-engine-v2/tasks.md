# Tasks
- [x] Task 1: Implement Feature Engineering & Model Persistence
  - [x] SubTask 1.1: Update `AnomalyDetector` in `anomaly.py` to calculate rolling variance and `diff()` for numeric columns. Append these as new features (e.g., `temp_diff`, `vib_var`) before passing to the pipeline.
  - [x] SubTask 1.2: Add `save(filepath)` and `load(filepath)` methods to `AnomalyDetector` using `joblib`.
  - [x] SubTask 1.3: Update `test_anomaly.py` to verify feature generation and model save/load functionality.
- [x] Task 2: Implement Incident Windowing
  - [x] SubTask 2.1: Create a utility function `group_anomalies_into_incidents(df)` that takes a dataframe with `is_anomaly == True` and groups consecutive timestamps into discrete windows (returning a list of dataframes or an aggregated summary).
  - [x] SubTask 2.2: Update `app.py` to display "Total Incidents Detected: X" instead of just passing raw anomalous rows.
- [x] Task 3: Configurable Rule Engine
  - [x] SubTask 3.1: Create `src/thermoneural/config/rules.yaml` containing the threshold definitions for Refrigerant Leak, Motor Overload, Bearing Failure, and Scroll Valve Leak.
  - [x] SubTask 3.2: Rewrite `analyze_root_cause` in `expert_system.py` to parse this YAML file using `pyyaml` (add to dependencies if needed).
  - [x] SubTask 3.3: The function should loop through the YAML rules dynamically and evaluate the incident peaks against them, returning the best match.
  - [x] SubTask 3.4: Update `test_expert_system.py` to mock or use the YAML file.

# Task Dependencies
- Task 3 requires adding `pyyaml` to `pyproject.toml`.
- Task 1, Task 2, and Task 3 can largely be developed in parallel, but integrating them into `app.py` must happen sequentially.