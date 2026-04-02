# Thermoneural World-Class Enterprise Upgrade Plan

> **For Claude / Trae:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the MVP into a "world-class" enterprise application. This involves upgrading the Streamlit dashboard to be highly insight-oriented with a premium UI, expanding the expert system to support multiple failure modes and financial impact analysis, and generating a detailed, multi-page PDF report.

**Architecture:**
1.  **Expert System (`expert_system.py`)**: Expand logic to detect 4 distinct failure modes (Scroll Valve Leak, Refrigerant Leak, Bearing Failure, Motor Overload). Add financial impact metrics (downtime cost, repair cost, total risk) to the output dictionary.
2.  **Dashboard UI (`app.py`)**: Implement a tabbed layout (Overview, Diagnostics, Financial Impact, Report). Use Streamlit columns, custom CSS, and advanced Plotly charts (e.g., radar charts for anomaly signatures, gauge charts for health scores) to make it "insight-oriented."
3.  **PDF Generation (`generator.py` & `report.html`)**: Upgrade to a multi-page PDF structure including a Cover Page, Executive Summary & Financials, Technical Methodology, and detailed charts.

**Tech Stack:** Python, Streamlit, Plotly, Pandas, WeasyPrint, Jinja2.

---

## 1. Current State Analysis
- **Expert System:** Only detects "Scroll Valve Leak" or "Generic Anomaly". Returns basic text strings (confidence, ETF, actions).
- **Dashboard UI:** A single scrolling page. Results are displayed as simple metric cards and basic line charts. Not insight-oriented or premium.
- **Reporting:** A single-page PDF with stacked subplots and an executive summary.

## 2. Proposed Changes

### Task 1: Expand Expert System & Financials (`src/thermoneural/rules/expert_system.py`)
**What:** Add 3 new failure modes and fixed financial cost estimates.
**How:**
- Calculate peak values for all 4 sensors: Temperature, Vibration, Pressure, Current.
- **Scroll Valve Leak:** Temp > 30, Vib > 1.5. (Downtime: $50k, Repair: $10k).
- **Refrigerant Leak:** Pressure < 90, Temp < 15. (Downtime: $100k, Repair: $25k).
- **Bearing Failure:** Vib > 2.0, Current > 20. (Downtime: $75k, Repair: $15k).
- **Motor Overload:** Temp > 35, Current > 25. (Downtime: $150k, Repair: $40k).
- Update the return dictionary to include `downtime_cost`, `repair_cost`, and `total_risk`.

### Task 2: Upgrade Synthetic Data Generator (`src/thermoneural/data/synthetic.py`)
**What:** Allow generating data that triggers the new failure modes.
**How:**
- Add a `failure_mode` parameter to `generate_sensor_data(days=30, failure_mode="Scroll Valve Leak")`.
- Based on the selection, inject the specific sensor spikes that correspond to the rules in Task 1.

### Task 3: Premium Dashboard UI Overhaul (`src/app.py`)
**What:** Rebuild the UI to be insight-oriented and tabbed.
**How:**
- Add a sidebar dropdown to select which synthetic failure mode to simulate.
- Use `st.tabs(["📊 Executive Dashboard", "🔍 Technical Diagnostics", "💰 Financial Impact", "📄 Report Generation"])`.
- **Executive Dashboard:** Health score (gauge chart), primary diagnosis, high-level financials.
- **Technical Diagnostics:** The detailed Plotly charts, anomaly scatter plots, and a radar chart showing the "anomaly signature" (which sensors deviated the most).
- **Financial Impact:** A bar chart or waterfall chart showing the cost breakdown of the failure vs. preventative maintenance.

### Task 4: Multi-Page PDF Report (`src/thermoneural/reports/templates/report.html` & `generator.py`)
**What:** Create a comprehensive, multi-page consulting document.
**How:**
- **CSS:** Add page breaks (`page-break-before: always;`).
- **Page 1 (Cover):** Large logo/title, date, confidential stamp.
- **Page 2 (Executive & Financial):** The summary, financial risk breakdown, and recommended actions.
- **Page 3 (Technical Analysis):** The stacked sensor charts and methodology explanation.

---

## 3. Implementation Tasks (Bite-Sized)

### Task 1: Update Synthetic Data Generator
**Files:**
- Modify: `src/thermoneural/data/synthetic.py`
- Modify: `tests/test_synthetic.py`

**Steps:**
1. Update `generate_sensor_data` to accept `failure_mode="Scroll Valve Leak"`.
2. Add `if/elif` blocks for "Refrigerant Leak" (drop pressure, drop temp), "Bearing Failure" (spike vib, spike current), "Motor Overload" (spike temp, spike current).
3. Update tests. Commit.

### Task 2: Update Expert System with Financials
**Files:**
- Modify: `src/thermoneural/rules/expert_system.py`
- Modify: `tests/test_expert_system.py`

**Steps:**
1. Extract peak `pressure_val` and `current_val`.
2. Implement the `if/elif` logic for the 4 failure modes.
3. Add `downtime_cost`, `repair_cost`, and `total_risk` to the return dictionaries (format as `"$50,000"`).
4. Update tests to cover new modes. Commit.

### Task 3: Overhaul Streamlit App (UI/UX)
**Files:**
- Modify: `src/app.py`

**Steps:**
1. Update sidebar to include a selectbox for `failure_mode` when generating synthetic data.
2. Implement `st.tabs`.
3. In Tab 1: Build a premium summary using `st.columns` and `st.metric`. Add a Plotly Gauge chart for "System Health Score" (e.g., 100 - confidence).
4. In Tab 2: Move the existing time-series charts here. Add a Plotly Radar chart comparing the peak z-scores of the 4 sensors.
5. In Tab 3: Display financial metrics and a simple bar chart of Costs.
6. In Tab 4: Place the PDF generation logic and download button.
7. Commit.

### Task 4: Upgrade PDF Template to Multi-Page
**Files:**
- Modify: `src/thermoneural/reports/templates/report.html`
- Modify: `src/thermoneural/reports/generator.py`

**Steps:**
1. Update HTML with `<div style="page-break-after: always;"></div>` to create distinct pages.
2. Add a Cover Page section.
3. Add a Financial Impact section referencing `{{ analysis.total_risk }}`.
4. Pass the new analysis keys from Python to Jinja2.
5. Commit.

### Task 5: Update E2E Tests
**Files:**
- Modify: `tests/test_e2e.py`

**Steps:**
1. Update Playwright script to click through the new tabs before downloading.
2. Assert the presence of new text like "Total Risk Exposure" and the specific failure mode selected.
3. Run `pytest tests/test_e2e.py -s`. Commit.

---

## Verification
- Run the E2E test.
- Open Streamlit, cycle through all 4 synthetic failure modes, verify the UI updates correctly, the radar charts render, and the multi-page PDF downloads successfully with all financial data intact.