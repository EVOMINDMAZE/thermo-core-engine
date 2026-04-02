# V1 Hardening Baseline Spec

## Why
The MVP demonstrates the core value of the Thermoneural Engine, but to evolve into a production-ready application (v1), the system must have reproducible environments, robust CI/CD, and strict data validation. This spec tackles "Phase 1 — Hardening baseline" from the PRD to ensure the application does not crash on malformed inputs and provides a stable foundation for future scalability.

## What Changes
- **BREAKING**: Move from `requirements.txt` to `pyproject.toml` to formally separate runtime and development dependencies.
- Integrate `ruff` for linting and formatting, along with a pre-commit configuration.
- Implement a GitHub Actions CI pipeline to run tests and linters on every change.
- Create a data contract module to validate incoming CSVs (missing timestamps, incorrect formats).
- Update the anomaly detection model to include a preprocessing pipeline (imputation and scaling) to handle real-world messy data seamlessly.

## Impact
- Affected specs: Architecture, CI/CD, Data Ingestion
- Affected code: `pyproject.toml`, `.github/workflows/ci.yml`, `src/thermoneural/data/validation.py` (new), `src/app.py`, `src/thermoneural/models/anomaly.py`

## ADDED Requirements
### Requirement: Data Contract Validation
The system SHALL validate uploaded CSV data against a defined contract and provide actionable errors.

#### Scenario: Success case
- **WHEN** user uploads a CSV missing a `timestamp` column
- **THEN** the system rejects the upload with a clear UI message instead of throwing a Python traceback.

### Requirement: Preprocessing Pipeline
The system SHALL standardise model input to handle missing values and scale variance.

#### Scenario: Success case
- **WHEN** a dataset with `NaN` sensor readings is provided
- **THEN** the `AnomalyDetector` imputes the missing values and scales the features before applying the Isolation Forest, preventing a crash.

## MODIFIED Requirements
### Requirement: Developer Environment
**Reason**: `requirements.txt` does not cleanly separate dev tooling from production dependencies.
**Migration**: Introduce `pyproject.toml` using a modern build backend (e.g., `setuptools` or `hatchling`) and remove `requirements.txt`.