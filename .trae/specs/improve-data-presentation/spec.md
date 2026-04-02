# Improve Data Presentation Spec

## Why
The current Streamlit dashboard displays raw data in a massive table and renders overlapping charts that can be overwhelming to non-technical users. To make the application world-class and insight-oriented, the data presentation must be streamlined. Users need to instantly grasp system health, financial risk, and the specific anomalies detected without digging through thousands of rows of data or deciphering cluttered charts.

## What Changes
- Hide the massive raw data table behind a collapsible expander.
- Introduce a tabbed layout (e.g., "Executive Summary", "Sensor Diagnostics") to separate high-level insights from deep technical data.
- Replace the basic `st.line_chart` with an interactive Plotly chart that clearly highlights anomalous data points directly on the actual sensor time-series (similar to the logic used in the PDF report).
- Enhance the "Analysis Results" section with a clearer visual hierarchy.

## Impact
- Affected specs: UI/UX Presentation
- Affected code: `src/app.py`

## ADDED Requirements
### Requirement: Tabbed Layout
The system SHALL provide a tabbed interface separating "Executive Summary" and "Detailed Diagnostics".

#### Scenario: Success case
- **WHEN** user runs the analysis
- **THEN** the primary tab shows the Failure Mode, Financial Risk, and Recommended Actions immediately.

## MODIFIED Requirements
### Requirement: Data Visualization
The time-series visualization SHALL use Plotly to clearly mark anomalous points in red over the standard sensor readings, avoiding cluttered overlapping lines.

## REMOVED Requirements
### Requirement: Default Raw Data Display
**Reason**: The raw data table is too large and pushes the actual insights below the fold.
**Migration**: Move the `st.dataframe()` into an `st.expander("View Raw Data")` so it is hidden by default but accessible if needed.