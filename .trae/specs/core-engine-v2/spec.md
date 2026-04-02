# Core Engine V2 Spec

## Why
The Thermoneural Engine has a solid baseline, but the logic is highly localized. It looks at points in isolation and relies on hardcoded thresholds in Python files. To support multiple equipment types, understand temporal context (e.g., "is the vibration getting worse?"), and operate efficiently on repeated runs, the engine needs advanced feature engineering, incident grouping, configurable rulesets, and model persistence.

## What Changes
- **Feature Engineering:** Add time-series derivatives (e.g., rate of change, rolling standard deviation) so the Isolation Forest understands temporal dynamics, not just static magnitudes.
- **Incident Windowing:** Group contiguous anomalous points into "Incident Windows". Instead of evaluating 50 individual anomalous rows, the Expert System will evaluate 1 distinct "Incident" that spanned 50 minutes.
- **Configurable Rule Engine:** Decouple business logic from `expert_system.py`. Move thresholds and failure mode mappings to an external `rules.yaml` file so they can be modified per client without code changes.
- **Model Persistence:** Use `joblib` or `pickle` to save the trained `AnomalyDetector` pipeline to disk, allowing future data streams to be predicted against a saved baseline without retraining.

## Impact
- Affected specs: ML Pipeline, Expert System Architecture
- Affected code:
  - `src/thermoneural/models/anomaly.py`
  - `src/thermoneural/rules/expert_system.py`
  - `src/thermoneural/config/rules.yaml` (New)

## ADDED Requirements
### Requirement: Temporal Feature Engineering
The system SHALL calculate rates of change (`diff`) and rolling variance for all numeric sensors prior to anomaly detection.

#### Scenario: Success case
- **WHEN** a dataset has a slowly rising temperature
- **THEN** the model flags it based on the anomalous rate of change, even if the absolute temperature hasn't crossed a catastrophic threshold yet.

### Requirement: Incident Windowing
The system SHALL group consecutive anomalous timestamps into a single discrete incident.

### Requirement: Configurable Rules
The system SHALL read diagnostic thresholds from a `rules.yaml` file rather than hardcoded Python logic.

### Requirement: Model Persistence
The system SHALL provide methods to save and load the trained `AnomalyDetector` pipeline to disk.

## MODIFIED Requirements
### Requirement: Expert System Evaluation
**Reason**: The current system evaluates a raw dataframe of anomalous rows.
**Migration**: The `analyze_root_cause` function must be updated to accept an "Incident" object or window and evaluate its peak values against the loaded `rules.yaml` configuration.