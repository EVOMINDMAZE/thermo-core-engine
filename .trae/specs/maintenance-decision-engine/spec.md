# Maintenance Decision Engine Spec

## Why
Currently, the application displays an "anomaly viewer" style dashboard. To truly act as a "maintenance decision engine," the application needs a prominent top summary block that instantly conveys the critical dimensions of a detected incident: the failure mode, confidence %, severity, likely root cause, recommended action, and downtime risk. This immediately aligns operations, reliability engineers, and management on the next steps without forcing them to interpret raw data.

## What Changes
- Add `severity`, `likely_root_cause`, and `downtime_risk` to all failure modes in the `rules.yaml` configuration.
- Standardize the `confidence` score as a strictly numeric value (0–100) instead of mixed text.
- Update the expert system rule engine to parse and return these new fields, ensuring robust backend fallbacks.
- Redesign the "Executive Summary" tab in the Streamlit UI to feature a unified, highly visible "Top Summary Block" combining Failure mode, Confidence %, Severity, Likely Root Cause, Recommended Action, and Downtime Risk.
- Define explicit severity ordering and color mappings (Normal, Low, Medium, High, Critical) in the UI.
- Update the generated PDF report template (`report.html`) to include these new insights and assert exact parity between UI summary and report output.

## Impact
- Affected specs: Expert System Configuration, Dashboard UI, PDF Reporting
- Affected code: 
  - `src/thermoneural/config/rules.yaml`
  - `src/thermoneural/rules/expert_system.py`
  - `src/app.py`
  - `src/thermoneural/reports/templates/report.html`

## ADDED Requirements
### Requirement: Maintenance Decision Summary Block
The system SHALL provide a consolidated top-level summary block displaying critical maintenance dimensions.

#### Scenario: Success case
- **WHEN** user runs an analysis and anomalies are detected
- **THEN** the Executive Summary tab immediately presents a block containing: Failure Mode, Confidence, Severity, Likely Root Cause, Recommended Action, and Total Downtime Risk.

## MODIFIED Requirements
### Requirement: Configurable Rules Schema
**Reason**: To support the new top summary block, failure definitions must include severity and root cause narratives.
**Migration**: Update `rules.yaml` to require `severity` (e.g., "Critical", "High", "Medium") and `likely_root_cause` string fields for every defined failure mode.