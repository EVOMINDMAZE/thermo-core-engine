# Tasks
- [x] Task 1: Implement Execution Logging & Tracing
  - [x] SubTask 1.1: Create `src/thermoneural/utils/logger.py` to configure a standard Python logger (console + file output).
  - [x] SubTask 1.2: Integrate logging into `app.py` to trace app startup, data uploads, and analysis triggers.
  - [x] SubTask 1.3: Add logging to `validation.py`, `anomaly.py`, and `expert_system.py` to record key decisions (e.g., "Found 45 anomalies", "Diagnosed Scroll Valve Leak").
- [x] Task 2: Advanced Data Preprocessing (Smoothing)
  - [x] SubTask 2.1: Update `AnomalyDetector` to accept a `smoothing_window` parameter.
  - [x] SubTask 2.2: Implement a rolling average (e.g., `df.rolling(window).mean()`) for all numeric sensor columns before passing them to the sklearn Pipeline.
- [x] Task 3: Auto-Calibrating ML Pipeline
  - [x] SubTask 3.1: Modify `AnomalyDetector.fit_predict` to calculate dataset variance/kurtosis.
  - [x] SubTask 3.2: Write logic to dynamically set the `contamination` parameter of the `IsolationForest` based on the calculated variance (e.g., higher variance = slightly higher contamination threshold).
  - [x] SubTask 3.3: Update tests to verify the dynamic calibration logic does not crash.
- [x] Task 4: Expand Failure Mode Catalog
  - [x] SubTask 4.1: Update `expert_system.py` to extract peak values for `pressure` and `current`.
  - [x] SubTask 4.2: Add logic for **Refrigerant Leak** (Drop in pressure, drop in temperature).
  - [x] SubTask 4.3: Add logic for **Bearing Failure** (Spike in vibration, spike in current).
  - [x] SubTask 4.4: Add logic for **Motor Overload** (Spike in temperature, spike in current).
  - [x] SubTask 4.5: Update `test_expert_system.py` to cover the new failure modes.

# Task Dependencies
- Task 1 should be completed first so subsequent tasks can utilize the logger.
- Task 2, Task 3, and Task 4 can be executed in parallel.