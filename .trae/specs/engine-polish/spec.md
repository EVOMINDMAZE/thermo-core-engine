# Thermoneural Engine Polish Spec

## Why
Before transitioning the Thermoneural Engine into a fully multi-tenant, self-service SaaS product, the core analytical engine must be upgraded. The current engine uses a basic, hardcoded Isolation Forest configuration and a limited rule set. To handle real-world, messy client data from diverse cryogenic systems with high reliability, the engine needs advanced preprocessing, an auto-calibrating ML pipeline, an expanded catalog of failure modes, and comprehensive execution logging. This ensures the output is robust enough to justify $10k-$25k consulting engagements.

## What Changes
- **Advanced Preprocessing:** Add rolling window calculations and signal smoothing (e.g., Savitzky-Golay or exponential moving averages) to reduce noise in high-frequency sensor data before it hits the ML model.
- **Auto-Calibrating ML Pipeline:** Refactor the `AnomalyDetector` to dynamically adjust the `contamination` parameter of the Isolation Forest based on the statistical variance of the specific dataset, rather than relying on a hardcoded default.
- **Expand Failure Mode Catalog:** Update the expert system to detect multiple specific failures (e.g., Refrigerant Leak, Bearing Failure, Motor Overload) by analyzing the interplay of Temperature, Pressure, Vibration, and Current.
- **Execution Logging & Tracing:** Implement a structured logging system (`logging` module) to trace data ingestion, preprocessing steps, model fitting, and rule evaluation, ensuring every diagnostic run leaves an auditable trail.

## Impact
- Affected specs: ML Pipeline, Diagnostic Rules, System Observability
- Affected code: 
  - `src/thermoneural/models/anomaly.py`
  - `src/thermoneural/rules/expert_system.py`
  - `src/thermoneural/utils/logger.py` (New)
  - `src/app.py`

## ADDED Requirements
### Requirement: Auto-Calibrating Anomaly Detection
The system SHALL dynamically tune its anomaly detection parameters based on the input dataset characteristics.

#### Scenario: Success case
- **WHEN** a client uploads a highly volatile dataset
- **THEN** the engine calculates the baseline variance and automatically adjusts the Isolation Forest `contamination` rate to prevent excessive false positives.

### Requirement: Advanced Preprocessing (Smoothing)
The system SHALL apply noise-reduction techniques to sensor data prior to anomaly detection.

#### Scenario: Success case
- **WHEN** a dataset contains high-frequency transient spikes (noise)
- **THEN** the preprocessing pipeline applies a rolling average/smoothing function so the model only flags sustained, structural anomalies.

### Requirement: Execution Traceability
The system SHALL log all major execution steps, parameters, and decisions to a structured log file.

## MODIFIED Requirements
### Requirement: Expanded Expert System
**Reason**: The current system only diagnoses "Scroll Valve Leak" or "Generic Anomaly".
**Migration**: The `analyze_root_cause` function must be expanded to evaluate `pressure` and `current` alongside `temperature` and `vibration` to map anomalies to at least 4 distinct failure modes.