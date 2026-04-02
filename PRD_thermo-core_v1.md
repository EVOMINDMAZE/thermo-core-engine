# Product Requirements Document (PRD) — Thermo-core (Thermoneural Engine) v1
**Document status:** Draft  
**Last updated:** 2026-04-01  
**Primary audience:** Engineering  
**Repository:** thermo-core / Thermoneural Engine  

---

## 1. Summary
Thermo-core (Thermoneural Engine) is an anomaly detection and root-cause analysis (RCA) tool for cryogenic systems. The current project is a Streamlit MVP that supports synthetic or CSV data, detects anomalies via Isolation Forest, applies a small rule engine to propose a failure mode, and generates a PDF report (HTML + WeasyPrint).

This PRD defines the scope of changes to evolve the MVP into a **production-shaped v1**: reproducible packaging and environments, robust data validation and preprocessing, scalable processing, richer RCA + explainability, report management, multi-user access controls, observability, and a deployment-ready architecture.

---

## 2. Goals (What v1 must achieve)
1. **Reliability & reproducibility:** A new developer or CI agent can set up, run, and test the project deterministically.
2. **Data contract & validation:** Uploaded data is validated, normalized, and errors are actionable; the system behaves correctly with missing/extra columns.
3. **Operational usefulness:** Outputs are trustworthy enough for engineering operations (clear anomaly windows, explanations, and consistent reporting).
4. **Productization:** Multi-user access, persisted history, report archive, and deployment-ready operations.
5. **Scalability path:** Clear separation between UI/API and compute so workloads can scale beyond a single process.

---

## 3. Non-goals (Explicitly out of scope for v1)
- Building a proprietary foundation model or training deep learning models end-to-end (v1 focuses on robust classical ML + domain logic).
- Real-time streaming ingestion at very high frequency (v1 targets batch uploads and scheduled ingestion; streaming is “vNext”).
- Fully automated corrective action execution (v1 recommends actions; it does not control equipment).
- Full “digital twin” simulation fidelity (synthetic data remains for demo/testing only).

---

## 4. Personas & use cases
### 4.1 Personas
- **Cryo Ops Engineer:** Uploads logs, needs fast triage, clear confidence, recommended actions, and shareable reports.
- **Reliability/Diagnostics Engineer:** Wants deeper diagnostics (feature contributions, anomaly windows, sensor trends, and RCA reasoning).
- **Maintenance Lead / Manager:** Consumes an “executive summary” view; cares about downtime risk and next steps.
- **Admin (Customer org):** Manages users, access, and system configuration.

### 4.2 Core use cases
1. Upload sensor logs → detect anomalies → produce RCA → generate & store report.
2. Compare incidents across time/equipment and search report history.
3. Configure thresholds, sensor mappings, units, and failure-mode rules per equipment type.
4. Export/share PDF report with auditability (who ran it, with which configuration).

---

## 5. Success metrics (v1)
Engineering-focused measurable outcomes:
- **Setup time:** Fresh machine to “run app + run tests” in < 10 minutes.
- **CI reliability:** ≥ 95% green rate on main branch (excluding flaky external dependencies).
- **Validation coverage:** ≥ 90% of common ingest errors produce actionable messages (missing timestamp, wrong units, NaNs, etc.).
- **Report determinism:** Same input + same config ⇒ identical report contents (excluding timestamps).
- **RCA usefulness:** For a curated validation dataset, top-1 failure mode matches ground truth ≥ agreed target (to be defined once real labels exist).

---

## 6. Product requirements

### 6.1 Data ingestion & contract (FR-100)
**Description:** Support robust ingestion from CSV (and optionally database/integration connectors in later phases), validate schema, and normalize units.

**Functional requirements**
- FR-100.1: Accept CSV upload with configurable delimiter and header row detection.
- FR-100.2: Require a time column (default: `timestamp`) and parse into timezone-aware datetime.
- FR-100.3: Support configurable sensor column mapping (e.g., temperature column might be `temp_C`, `T1`, etc.).
- FR-100.4: Validate numeric ranges and missingness; provide clear user-facing errors/warnings.
- FR-100.5: Unit normalization (e.g., °C/°F, psi/bar) via configuration.
- FR-100.6: Persist uploaded raw data and normalized dataset for reproducibility (see storage requirements).

**Acceptance criteria**
- Uploading a CSV with missing `timestamp` fails with a clear message and remediation steps.
- Uploading a CSV with missing optional sensors (e.g., vibration absent) still runs analysis; UI and reporting degrade gracefully.

---

### 6.2 Preprocessing & feature pipeline (FR-200)
**Description:** Standardize the model input and make anomaly detection robust to scale and missing values.

**Functional requirements**
- FR-200.1: Implement preprocessing pipeline: imputation strategy, scaling/normalization, and optional smoothing/windowing.
- FR-200.2: Allow selecting feature set and window size (UI + API).
- FR-200.3: Version the pipeline configuration (stored with each run).

**Acceptance criteria**
- Isolation Forest (or replacement model) uses scaled features by default; feature dominance due to units is eliminated.
- Pipeline config is recorded and visible in run metadata and report appendix.

---

### 6.3 Anomaly detection engine (FR-300)
**Description:** Provide a pluggable anomaly detection interface with configurable algorithms and calibration.

**Functional requirements**
- FR-300.1: Keep the existing Isolation Forest path, but make it pluggable (strategy pattern).
- FR-300.2: Provide calibration utilities to tune contamination/thresholds using baseline data (per equipment type).
- FR-300.3: Produce consistent outputs:
  - `is_anomaly` (boolean)
  - `anomaly_score` (float, higher = more anomalous OR clearly documented convention)
  - anomaly windows/segments (grouped contiguous anomalies)

**Acceptance criteria**
- A run produces both point-level anomalies and window-level incident summaries.

---

### 6.4 Root-cause analysis (rules + explainability) (FR-400)
**Description:** Expand beyond a single rule to a multi-failure-mode engine with explanations.

**Functional requirements**
- FR-400.1: Support a catalog of failure modes (e.g., valve leak, bearing wear, sensor drift, insulation degradation).
- FR-400.2: Each failure mode includes:
  - name, description
  - triggering conditions
  - confidence computation logic
  - recommended actions
  - evidence/explanation string(s)
- FR-400.3: Provide an “unknown / ambiguous” path with next diagnostic steps.
- FR-400.4: Support equipment-specific rulesets (by system type, model, or customer configuration).

**Acceptance criteria**
- For each analysis, the UI shows: primary failure mode, confidence, and a short explanation (evidence bullets).
- Report includes an “Evidence” section describing why the system decided that failure mode.

---

### 6.5 Reporting (PDF + run metadata) (FR-500)
**Description:** Generate a production-quality report, store it, and allow retrieval.

**Functional requirements**
- FR-500.1: Keep PDF generation (Jinja2 → HTML → WeasyPrint), but ensure templates handle missing sensors gracefully.
- FR-500.2: Report includes:
  - Executive summary
  - Incident timeline (anomaly windows)
  - Sensor plots (only available sensors)
  - RCA result (failure mode + confidence + evidence)
  - Actions + estimated impact (configurable)
  - Appendix: run configuration, data contract summary, model version, ruleset version
- FR-500.3: Persist generated reports and link them to runs.

**Acceptance criteria**
- Report generation never crashes when one or more sensors are absent; sections are omitted or marked “N/A”.

---

### 6.6 UI/UX (v1 product UI) (FR-600)
**Description:** Provide a usable workflow for both “executive” and “technical” users and support report history.

**Functional requirements**
- FR-600.1: Guided upload with data contract display and validation results.
- FR-600.2: Analysis configuration panel (feature selection, thresholds, equipment type, ruleset).
- FR-600.3: Results view:
  - incident list (anomaly windows)
  - click-to-zoom charts for a selected incident
  - RCA summary + evidence
- FR-600.4: Report history:
  - searchable by date/equipment/failure mode
  - ability to download prior PDFs

**Notes**
- Streamlit may remain acceptable for v1 if requirements are met; otherwise v1 can split to a thin web UI + API.

---

### 6.7 Authentication, authorization, and tenancy (FR-700)
**Description:** Add multi-user access and isolate customer data.

**Functional requirements**
- FR-700.1: Authentication (options: passwordless email link, SSO later, or basic email/password for v1).
- FR-700.2: Roles:
  - Admin: manage org, users, configs
  - Engineer: run analyses, view/download reports
  - Viewer: view/download reports only
- FR-700.3: Multi-tenant separation: each org sees only its own uploads/runs/reports.
- FR-700.4: Audit log entries for: login, upload, analysis run, report download, config changes.

**Acceptance criteria**
- A user from Org A cannot access runs/reports from Org B (validated via API tests).

---

### 6.8 Storage & persistence (FR-800)
**Description:** Persist datasets, runs, configs, and reports.

**Functional requirements**
- FR-800.1: Persist:
  - raw uploads (original CSV)
  - normalized dataset (optional, can be derived but must be reproducible)
  - run metadata (who/when/config/model version)
  - RCA outputs
  - report PDFs
- FR-800.2: Support a simple initial storage stack:
  - Postgres for metadata
  - Object storage for files (S3-compatible) OR local filesystem for single-node deployments

---

### 6.9 Processing architecture & scalability (FR-900)
**Description:** Support asynchronous jobs for heavy runs and report generation.

**Functional requirements**
- FR-900.1: Analysis runs execute as jobs (queue/worker), not blocking the UI thread.
- FR-900.2: Job status: queued/running/succeeded/failed with error details.
- FR-900.3: Ability to cancel jobs (best-effort).

**Acceptance criteria**
- UI can trigger analysis and return immediately; results appear when ready.

---

## 7. Non-functional requirements (NFR)

### 7.1 Quality, reliability, maintainability
- NFR-1: Deterministic environment setup (lockfile or pinned deps).
- NFR-2: Clear packaging: `pyproject.toml` with defined entrypoints and tooling config.
- NFR-3: Linting + formatting: ruff/black (or ruff-only), plus pre-commit hooks.
- NFR-4: Type checking baseline (mypy or pyright) for core modules.
- NFR-5: Structured logging and consistent error handling.

### 7.2 Security
- NFR-6: Secure file upload handling (size limits, content checks, storage isolation).
- NFR-7: Secrets management via environment variables; no secrets in repo.
- NFR-8: Audit logs for sensitive actions.

### 7.3 Observability
- NFR-9: Metrics for job duration, failures, report generation time.
- NFR-10: Tracing/correlation IDs for runs and reports.

---

## 8. Developer experience & repository changes

### 8.1 Packaging and environment (DEV-100)
- DEV-100.1: Add `pyproject.toml` (recommended) defining:
  - project metadata
  - dependencies
  - optional dev dependencies (e.g., playwright, pymupdf)
  - tooling config (pytest, ruff, etc.)
- DEV-100.2: Split dependencies into runtime vs dev:
  - runtime: streamlit, pandas, numpy, scikit-learn, plotly, weasyprint, jinja2
  - dev/test: pytest, playwright, pymupdf, etc.
- DEV-100.3: Remove `venv/` from repo and ensure `.gitignore` covers it.

### 8.2 Testing & CI (DEV-200)
- DEV-200.1: Make E2E tests optional:
  - skip if Playwright isn’t installed
  - separate CI job for E2E with required deps
- DEV-200.2: Add CI pipeline (GitHub Actions or equivalent):
  - unit tests
  - lint/type checks
  - optional e2e job
- DEV-200.3: Ensure “scripts” are not collected as tests unless intended (rename or configure pytest).

---

## 9. Rollout plan (phased, since timeline is “TBD”)
### Phase 1 — “Hardening baseline” (foundation)
- Packaging + dependency split + remove `venv/`
- Add linting/formatting and minimal CI
- Make E2E optional and stable
- Data validation + preprocessing pipeline

### Phase 2 — “Product usefulness”
- Anomaly windows + incident list
- Expanded RCA rules + evidence
- Robust report template + run metadata appendix

### Phase 3 — “Productization”
- Persistence layer (Postgres + object store)
- Auth/RBAC + tenancy + audit logs
- Async jobs + worker queue

### Phase 4 — “Scale & integrations”
- Integrations (data connectors)
- Monitoring dashboards and operational alerts

---

## 10. Dependencies & open questions
### Dependencies
- Decision: keep Streamlit for v1 vs migrate to a dedicated API + frontend.
- Choice of job queue (Celery/RQ/Arq) and storage (S3/local).
- Labelled dataset availability for RCA evaluation and calibration.

### Open questions (must be answered to finalize v1)
1. What are the target customer environments (on-prem vs cloud, security constraints)?
2. Expected data sizes (rows per upload, sensors per asset, frequency)?
3. Which failure modes are the initial “must-have” list for v1?
4. Preferred authentication method for early customers?
5. Reporting requirements: branding, signatures, compliance, retention policies?

---

## 11. Appendix — Current MVP notes (baseline reference)
- UI entrypoint: `src/app.py` (Streamlit)
- Model: `src/thermoneural/models/anomaly.py` (IsolationForest)
- RCA: `src/thermoneural/rules/expert_system.py` (single rule demo)
- Reporting: `src/thermoneural/reports/generator.py` + `templates/report.html` (WeasyPrint)
- Tests: unit tests exist; E2E depends on Playwright and is not declared in runtime requirements.

