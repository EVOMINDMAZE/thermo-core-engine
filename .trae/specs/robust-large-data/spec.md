# Robust Large Data Processing Spec

## Why
The application currently crashes when processing large datasets (like the 1.5 million row MetroPT-3 dataset) due to two issues:
1. `MessageSizeError`: Attempting to send a massive 200MB+ DataFrame to the browser for the "Raw Data Preview" and plotting millions of points in Plotly exceeds Streamlit's WebSocket message limits.
2. `KeyError: 'vibration'`: The Technical Diagnostics tab hardcodes expected sensors (temperature, pressure, vibration, current). If a user maps a dataset that lacks one of these (e.g., no vibration data), the app crashes when attempting to render the Peak Values table or the Radar Chart.

## What Changes
- Limit the "Raw Data Preview" to display only the first 1,000 rows.
- Increase the `server.maxMessageSize` configuration in `.streamlit/config.toml` to prevent WebSocket crashes on large charts.
- Implement intelligent downsampling for the Plotly charts: if the dataset is massive, downsample the "normal" background points to keep the browser responsive, while ensuring 100% of the anomalous points are still plotted.
- Make the `render_tech_diag` function fully dynamic so it only attempts to chart and summarize sensor columns that actually exist in the mapped dataset.

## Impact
- Affected specs: UI/UX, Data Visualization, Performance
- Affected code:
  - `src/app.py`
  - `.streamlit/config.toml`

## ADDED Requirements
### Requirement: Dynamic Sensor Rendering
The Technical Diagnostics tab SHALL dynamically adapt to the available sensors, preventing KeyErrors.

#### Scenario: Success case
- **WHEN** a user uploads a dataset containing only `temperature` and `current`
- **THEN** the Peak Values table, Radar Chart, and Trend Subplots only render those two axes, and do not crash looking for `pressure` or `vibration`.

### Requirement: Large Dataset Visualization
The system SHALL safely render visualizations for datasets exceeding 1 million rows without crashing the browser.

#### Scenario: Success case
- **WHEN** a user uploads a 1.5M row dataset
- **THEN** the preview is truncated, and the Plotly charts downsample the baseline data to maintain a fast, responsive UI.