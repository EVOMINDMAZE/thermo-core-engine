# Thermoneural Report Overhaul - Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to outline the technical specifications and requirements for upgrading the Thermoneural Engine's PDF reporting module. The goal is to transition the current basic, unformatted HTML/PDF output into a highly professional, enterprise-grade Forensic Root-Cause Analysis (RCA) Report suitable for client delivery and consulting engagements.

### 1.2 Scope
This specification covers changes to three primary components:
1.  **The Rule Engine (`expert_system.py`)**: Expanding the data payload to include quantitative metrics.
2.  **The Matplotlib Generator (`generator.py`)**: Redesigning the data visualization logic.
3.  **The PDF Template (`report.html`)**: Complete UI/UX overhaul of the document layout and styling.

### 1.3 Audience
- Solopreneur/Founder (End-User)
- Prospective Enterprise Clients (Consumers of the generated PDF)

---

## 2. Functional Requirements

### 2.1 Enhanced Analysis Payload (Rule Engine)
- **FR-1.1**: The `analyze_root_cause` function MUST calculate the peak (maximum) temperature and vibration values from the subset of data flagged as anomalous.
- **FR-1.2**: The function MUST return these values formatted as strings with appropriate units (e.g., `peak_temp: "35.2 °C"`, `peak_vib: "2.10 mm/s"`).
- **FR-1.3**: In the event of no anomalies, the function MUST return `"N/A"` for these metric fields.

### 2.2 Separated Subplot Visualization (Report Generator)
- **FR-2.1**: The system MUST NOT overlay Temperature and Vibration on a single dual-axis plot.
- **FR-2.2**: The system MUST generate a figure containing two vertically stacked subplots sharing the same X-axis (Timestamp).
- **FR-2.3**: The top subplot MUST display the Temperature time-series (blue line) and highlight anomalies with distinct red 'X' markers.
- **FR-2.4**: The bottom subplot MUST display the Vibration time-series (green line) and highlight anomalies with distinct dark red '+' markers.
- **FR-2.5**: Both subplots MUST include background gridlines (alpha=0.3) for readability.

### 2.3 Professional Template Overhaul (HTML/CSS)
- **FR-3.1**: The template MUST include a formal header containing the company name ("Thermoneural"), document title ("Forensic Root-Cause Analysis Report"), and the dynamic generation date.
- **FR-3.2**: The template MUST include an **"Executive Summary"** section that clearly states the primary finding (Failure Mode) and Confidence Score in a conversational, easy-to-read format.
- **FR-3.3**: The template MUST include a **"Metrics Breakdown"** section (e.g., a stylized table or grid) showing the Peak Temperature and Peak Vibration recorded during the anomaly window.
- **FR-3.4**: The template MUST include a **"Recommended Actions"** section prominently displayed, indicating immediate next steps and Estimated Time to Failure (ETF).
- **FR-3.5**: The template MUST include a **"Chart Explanation"** section placed immediately below the data visualization, explaining to a non-technical reader what the blue/green lines and red markers signify.

---

## 3. Non-Functional Requirements

### 3.1 Design & Aesthetics
- **NFR-1.1**: The PDF MUST utilize a clean, modern, sans-serif font stack (e.g., Arial, Helvetica, sans-serif).
- **NFR-1.2**: The color palette MUST be professional (e.g., dark slate blues `#2c3e50` for headers, subtle grays `#f8f9fa` for summary boxes, and stark reds for critical alerts).
- **NFR-1.3**: The document MUST have appropriate padding, margins, and line spacing to avoid a cramped appearance.

### 3.2 Performance
- **NFR-2.1**: The generation of the Matplotlib charts and the WeasyPrint PDF rendering MUST complete within 5 seconds for a standard 90-day dataset (approx 2,160 rows).

### 3.3 Reliability & Testing
- **NFR-3.1**: The existing `test_expert_system.py` MUST be updated to verify the presence of `peak_temp` and `peak_vib` keys.
- **NFR-3.2**: The existing Playwright E2E test (`test_e2e.py`) MUST be updated to parse the PDF and assert the existence of the new sections ("Executive Summary", "Metrics Breakdown").

---

## 4. Architecture & Interface Definitions

### 4.1 Dictionary Interface (`analyze_root_cause`)
**Current:**
```python
{
  "failure_mode": str,
  "confidence": float,
  "etf": str,
  "actions": str
}
```
**Proposed:**
```python
{
  "failure_mode": str,
  "confidence": float,
  "etf": str,
  "actions": str,
  "peak_temp": str,  # NEW
  "peak_vib": str    # NEW
}
```

### 4.2 Template Variables (`report.html`)
The Jinja2 environment will receive:
- `analysis`: The dictionary defined in 4.1.
- `plot_path`: Local file URI to the generated PNG.
- `generation_date`: String representing the current date (e.g., "March 31, 2026").

---

## 5. Execution Strategy

If the user approves this specification, the Agent will immediately transition out of Plan mode and execute the following sequence:
1. Update `expert_system.py` and run tests.
2. Update `generator.py` to implement the stacked subplots.
3. Completely rewrite `report.html` with the new CSS and structure.
4. Update and execute the E2E Playwright test to verify the PDF text structure.
5. Provide the user with instructions to view the live Streamlit preview and download the new professional report.