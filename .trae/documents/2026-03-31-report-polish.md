# Thermoneural Report Polish Implementation Plan

> **For Claude / Trae:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign the generated PDF Forensic Report to make it a professional, enterprise-ready deliverable. The report will include executive summaries, clear chart explanations, metric breakdowns, professional branding, and a much cleaner data visualization approach using separated subplots.

**Architecture:** 
1. Update `expert_system.py` to return the peak metrics that triggered the anomaly, so they can be injected into the report.
2. Update `generator.py` to create stacked subplots (one for Temperature, one for Vibration) instead of a messy dual-axis plot.
3. Completely overhaul `report.html` (the Jinja2 template) to include CSS styling for a cover page feel, executive summary, metrics breakdown, and a "How to Read this Chart" legend.

**Tech Stack:** Python, Pandas, Matplotlib, Jinja2, WeasyPrint, HTML/CSS.

---

## 1. Current State Analysis
- **Graph:** Overlays Temperature and Vibration on a single dual-axis plot. It looks cluttered when there are many data points (like 90 days), and the red markers get lost.
- **Template:** A very basic HTML file with a single `<h1>` and an unordered list of the analysis results. It lacks any explanatory text, branding, or professional formatting.
- **Analysis Data:** Currently only returns `failure_mode`, `confidence`, `etf`, and `actions`. It does not pass the actual anomalous metric values to the report.

## 2. Proposed Changes

### Task 1: Enhance Analysis Payload (`src/thermoneural/rules/expert_system.py`)
**What:** Modify `analyze_root_cause` to include the peak temperature and vibration values in the returned dictionary.
**Why:** To populate the "Metrics Breakdown" section in the report.
**How:**
- Add `peak_temp` and `peak_vib` keys to the returned dictionary.
- Format them nicely (e.g., `f"{temp_val:.1f} °C"`, `f"{vib_val:.2f} mm/s"`).

### Task 2: Redesign Data Visualization (`src/thermoneural/reports/generator.py`)
**What:** Refactor the matplotlib generation to use stacked subplots.
**Why:** Separating the charts makes it instantly readable. Temperature gets its own chart, Vibration gets its own chart.
**How:**
- Use `plt.subplots(2, 1, figsize=(10, 8), sharex=True)`.
- Plot Temperature and its anomalies on `ax1`.
- Plot Vibration and its anomalies on `ax2`.
- Add clear titles, grids (`ax.grid(True, alpha=0.3)`), and legends to both.

### Task 3: Overhaul HTML/CSS Template (`src/thermoneural/reports/templates/report.html`)
**What:** Rewrite the template to look like a premium consulting report.
**Why:** To build trust with enterprise clients.
**How:**
- Add a professional Header (Company Name, Report Date, "Confidential").
- Add an **Executive Summary** paragraph dynamically explaining the failure mode.
- Add a **Metrics Breakdown** table showing the baseline vs. the peak anomaly values.
- Add the stacked charts.
- Add a **Chart Explanation** section below the chart explaining the blue/green lines and the red markers.
- Use modern, clean CSS (sans-serif, good line-height, subtle borders).

---

## 3. Implementation Tasks (Bite-Sized)

### Task 1: Update Expert System
**Files:**
- Modify: `src/thermoneural/rules/expert_system.py`
- Modify: `tests/test_expert_system.py`

**Step 1:** Update `analyze_root_cause` to return peak metrics.
```python
# In the return dict for Scroll Valve Leak:
"peak_temp": f"{temp_val:.1f} °C",
"peak_vib": f"{vib_val:.2f} mm/s",
# In the return dict for Generic Anomaly / Normal:
"peak_temp": "N/A",
"peak_vib": "N/A",
```
**Step 2:** Update tests to assert these new keys exist.
**Step 3:** Commit.

### Task 2: Update Matplotlib Generator
**Files:**
- Modify: `src/thermoneural/reports/generator.py`

**Step 1:** Replace the dual-axis `ax1.twinx()` code with `fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)`.
**Step 2:** Plot Temp on `ax1` and Vib on `ax2`. Add `ax1.grid(True)` and `ax2.grid(True)`.
**Step 3:** Adjust the legend to sit nicely on each subplot.
**Step 4:** Update `generate_pdf_report` to pass the current date to the Jinja2 template (`from datetime import datetime`).
**Step 5:** Commit.

### Task 3: Overhaul Report Template
**Files:**
- Modify: `src/thermoneural/reports/templates/report.html`

**Step 1:** Add modern CSS (e.g., `.header`, `.summary-box`, `.metrics-table`).
**Step 2:** Structure the HTML:
- Header with "Thermoneural Engine" and `{{ generation_date }}`.
- Executive Summary `div`.
- Metrics Breakdown `table`.
- Actions `div`.
- Chart `img`.
- Chart Explanation `div` ("The charts above represent the historical sensor data...").
**Step 3:** Commit.

### Task 4: Run E2E Test
**Files:**
- Modify: `tests/test_e2e.py` (if necessary to check for new text like "Executive Summary")
- Run: `pytest tests/test_e2e.py -s`

---

## Verification
- Run the E2E test.
- Open the Streamlit app, generate data, run analysis, download the PDF.
- Visually inspect the PDF to ensure it looks like a professional consulting deliverable with two distinct, readable graphs and clear explanations.