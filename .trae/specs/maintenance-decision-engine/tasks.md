# Tasks
- [x] Task 1: Update Rule Engine Configuration
  - [x] SubTask 1.1: Add `severity`, `likely_root_cause`, and `downtime_risk` fields to all failure modes in `src/thermoneural/config/rules.yaml`.
  - [x] SubTask 1.2: Standardize the `confidence` field to strictly be a number from 0–100 (int/float), not mixed text.
  - [x] SubTask 1.3: Update `expert_system.py` to parse these new fields and return them in the analysis dictionary (including robust backend fallbacks for "Generic Anomaly" and "Normal Operation").
  - [x] SubTask 1.4: Update `test_expert_system.py` to assert the presence of these new fields (`severity`, `likely_root_cause`, `downtime_risk`) and the standardized numeric confidence type.
- [x] Task 2: Refactor UI (Top Summary Block)
  - [x] SubTask 2.1: Update `app.py` in the "Executive Summary" tab to replace the scattered metrics with one cohesive, prominent "Top Summary Block".
  - [x] SubTask 2.2: Ensure the block exactly displays: Failure mode, confidence %, severity, likely root cause, recommended action, and downtime risk.
  - [x] SubTask 2.3: Define severity ordering and map specific colors: Normal (Green), Low (Blue), Medium (Yellow), High (Orange), Critical (Red) using Streamlit's alert components (`st.success`, `st.info`, `st.warning`, `st.error`) or custom HTML/CSS.
- [x] Task 3: Update PDF Report & E2E Tests
  - [x] SubTask 3.1: Update the generated PDF report template (`src/thermoneural/reports/templates/report.html`) to include `severity`, `likely_root_cause`, and `downtime_risk` in the Executive Summary section.
  - [x] SubTask 3.2: Update `test_e2e.py` to verify the generated PDF report shows the exact same values for Failure Mode, Confidence, Severity, Root Cause, Action, and Risk as displayed on the on-screen summary (assert exact parity).

# Task Dependencies
- Task 2 depends on Task 1.
- Task 3 depends on Task 1.