# Thermoneural Pragmatic Enterprise Upgrade Plan

> **For Claude / Trae:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Evolve the MVP into a pragmatic, enterprise-ready application while prioritizing immediate client validation. We will integrate high-value financial metrics, ensure the engine can handle real-world data (via MetroPT-3 validation), and generate the necessary outreach materials to secure the first pilot.

**Strategy:** Balance polish with pragmatism. Avoid over-engineering the UI with tabs and radar charts for now. Instead, focus on the core value proposition: explaining the financial impact of failures and proving the engine works on non-synthetic datasets.

**Tech Stack:** Python, Streamlit, Plotly, Pandas, WeasyPrint, Jinja2.

---

## 1. Current State Analysis
- **Expert System:** Detects "Scroll Valve Leak" or "Generic Anomaly". Returns basic text strings (confidence, ETF, actions). Lacks financial context.
- **Data Ingestion:** Tuned tightly to the specific bounds of our synthetic data generator. Not yet proven on a messy, real-world public dataset.
- **Dashboard UI:** A clean, single-page layout that gets the job done but lacks the high-impact "cost" numbers that enterprise buyers care about.
- **Outreach:** The engine can generate a sample report, but there are no standardized email templates or structured outreach assets ready to send.

## 2. Proposed Changes

### Change 1: Financial Impact Analysis (High Value / Low Effort)
- **Update `expert_system.py`** to return hardcoded `downtime_cost`, `repair_cost`, and `total_risk` based on the detected failure mode.
- **Update the Dashboard & PDF Report** to prominently display these financial figures, translating technical anomalies into business risk.

### Change 2: Real-Data Readiness (MetroPT-3 Validation)
- **Create a data ingestion pipeline** that can automatically download, format, and process the public MetroPT-3 dataset (a well-known predictive maintenance dataset).
- **Test the Isolation Forest** against this real data to ensure it doesn't crash on missing values or unexpected scales, proving the pipeline is robust for actual client CSVs.

### Change 3: Immediate Outreach Asset Generation
- **Generate `docs/outreach_assets.md`** containing proven cold-email templates, a LinkedIn content plan, and instructions on how to use the current MVP to generate a "Sample Report" PDF to attach to these emails.

---

## 3. Implementation Tasks (Bite-Sized)

### Task 1: Add Financial Impact to Expert System
**Files:**
- Modify: `src/thermoneural/rules/expert_system.py`
- Modify: `tests/test_expert_system.py`

**Steps:**
1. Update `analyze_root_cause` to include financial keys in the return dictionary.
   - *Scroll Valve Leak:* `downtime_cost: "$50,000"`, `repair_cost: "$10,000"`, `total_risk: "$60,000"`.
   - *Generic Anomaly:* `downtime_cost: "TBD"`, `repair_cost: "TBD"`, `total_risk: "High Risk"`.
   - *Normal:* `$0`.
2. Update tests to assert the new financial keys exist.
3. Commit.

### Task 2: Display Financials in UI & PDF
**Files:**
- Modify: `src/app.py`
- Modify: `src/thermoneural/reports/templates/report.html`

**Steps:**
1. In `app.py`, update the `st.metric` columns to display the `total_risk` prominently.
2. In `report.html`, add a "Financial Risk Assessment" section below the Executive Summary that highlights the Downtime Cost, Repair Cost, and Total Exposure.
3. Commit.

### Task 3: Real-Data Readiness (MetroPT-3 Script)
**Files:**
- Create: `scripts/test_real_data.py`

**Steps:**
1. Write a standalone script that downloads a small sample of the MetroPT-3 dataset (or uses a provided subset if downloading is too slow).
2. Map the MetroPT-3 columns (e.g., pressure, temperature, motor current) to our engine's expected format.
3. Pass the dataframe through `AnomalyDetector.fit_predict()`.
4. Ensure the script completes without throwing `ValueError` or scaling errors, proving the Isolation Forest handles real-world variance.
5. Commit.

### Task 4: Generate Outreach Materials
**Files:**
- Create: `docs/outreach_assets.md`

**Steps:**
1. Write 2 variations of a cold email targeting Plant Managers / Maintenance Directors at LNG/Cryo facilities. The email must offer a free, zero-risk "Forensic Failure Audit" on their historical CSV logs.
2. Write a short LinkedIn post announcing the Thermoneural Engine MVP.
3. Commit.

### Task 5: Update E2E Tests
**Files:**
- Modify: `tests/test_e2e.py`

**Steps:**
1. Update the Playwright script to verify the PDF now contains the text "Financial Risk Assessment" and "$60,000".
2. Run `pytest tests/test_e2e.py -s`. Commit.

---

## 4. Verification
- The automated E2E test passes.
- `python scripts/test_real_data.py` successfully processes real-world data without crashing.
- `docs/outreach_assets.md` is populated and ready for the founder to copy-paste.

---

## 5. Immediate Next Steps for Outreach
*(Actions the founder can take today, even before these coding tasks finish)*

1. **Generate the Sample Asset:** Open the Streamlit app right now, click "Generate Synthetic Data", run the analysis, and download the "Thermoneural_RCA_Report.pdf". This is your core marketing asset.
2. **Build the Target List:** Go to LinkedIn or industry directories and build a list of 20 local "Maintenance Managers" or "Reliability Engineers" at mid-stream cryogenic facilities or LNG terminals within a 200-mile radius.
3. **Warm Up the Network:** Message former professors, colleagues, or local repair shops. Tell them you have built an AI tool specifically for scroll compressors and ask if they know anyone who recently suffered an unplanned downtime event.
4. **Prepare for the "Yes":** When a prospect says "Sure, here is our data", ensure you have an NDA ready to sign, as industrial sensor logs are highly confidential.