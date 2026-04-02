# Phase 2 Upgrades Spec

## Why
The Thermoneural Engine currently acts as a robust single-asset maintenance decision engine using pure ML (Isolation Forest) and static rules. To reach true enterprise maturity, it must validate data against the laws of physics, quantify its own uncertainty to build operator trust, maintain an audit log of all predictions, and support multi-asset fleet views so plant managers can prioritize maintenance across dozens of machines.

## What Changes
- **Physics-Informed Rules:** Introduce a `physics_checks.py` module to validate sensor data against first-principle cryogenic relationships (e.g., Temperature-Pressure correlations, expected compressor efficiency). These violations will be fed into the ML model as new features and displayed as evidence in the RCA.
- **Uncertainty Quantification (UQ):** Implement bootstrapping or conformal prediction on the Isolation Forest to output a confidence interval (e.g., "85% ± 5%") for the anomaly score, rather than a single absolute number.
- **Audit Log & Prediction History:** Migrate from simple text logging to a structured SQLite database (`history.db`) that records every run's inputs, parameters, detected incidents, and RCA outputs for historical querying.
- **Multi-Asset / Fleet View:** Update the data ingestion and UI to accept an `asset_id` column. Create a new "Fleet Overview" dashboard tab that ranks all assets by total downtime risk.

## Impact
- Affected specs: ML Pipeline, Expert System, UI/UX, Data Storage
- Affected code:
  - `src/thermoneural/rules/physics_checks.py` (New)
  - `src/thermoneural/models/anomaly.py`
  - `src/thermoneural/storage/db.py` (New)
  - `src/app.py`
  - `src/thermoneural/data/synthetic.py`

## ADDED Requirements
### Requirement: Physics-Informed ML
The system SHALL calculate physics residuals (theoretical vs. actual) and use them as features for the Isolation Forest.

#### Scenario: Success case
- **WHEN** a pressure sensor drifts while temperature remains constant (violating gas laws)
- **THEN** the `physics_checks.py` flags the residual, and the ML model detects the anomaly even if the absolute pressure hasn't breached a static threshold.

### Requirement: Uncertainty Intervals
The system SHALL provide a ± confidence interval for its anomaly predictions.

### Requirement: Audit Database
The system SHALL store structured run results in a local SQLite database.

### Requirement: Fleet Ranking
The system SHALL aggregate risk across multiple `asset_id`s and display a sorted fleet-risk table.

## MODIFIED Requirements
### Requirement: Synthetic Data Generation
**Reason**: To test the fleet view, the synthetic generator must create data for multiple machines.
**Migration**: Update `generate_sensor_data` to accept `num_assets` and return a dataframe with an `asset_id` column.