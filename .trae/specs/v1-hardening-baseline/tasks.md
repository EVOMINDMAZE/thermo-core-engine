# Tasks
- [x] Task 1: Setup Packaging & Tooling (DEV-100)
  - [x] SubTask 1.1: Create `pyproject.toml` with project metadata, defining runtime dependencies (`streamlit`, `pandas`, `scikit-learn`, `plotly`, `weasyprint`, `jinja2`) and dev dependencies (`pytest`, `playwright`, `pymupdf`, `pytest-playwright`, `ruff`).
  - [x] SubTask 1.2: Configure `ruff` in `pyproject.toml` for linting and formatting.
  - [x] SubTask 1.3: Delete `requirements.txt` and ensure `.gitignore` excludes `venv/`.
- [x] Task 2: Continuous Integration (DEV-200)
  - [x] SubTask 2.1: Create `.github/workflows/ci.yml` to trigger on push to `main` and pull requests.
  - [x] SubTask 2.2: Configure CI to run `ruff check`, `ruff format --check`, and `pytest tests/`.
- [x] Task 3: Data Ingestion & Contract Validation (FR-100)
  - [x] SubTask 3.1: Create `src/thermoneural/data/validation.py` with a `validate_sensor_data(df)` function.
  - [x] SubTask 3.2: Ensure validation checks for the existence of a time column (and parses to datetime), checks for valid numeric sensors, and returns a tuple `(is_valid: bool, error_message: str, df: pd.DataFrame)`.
  - [x] SubTask 3.3: Integrate `validate_sensor_data` into `src/app.py` so the UI surfaces `st.error()` on invalid uploads and halts analysis gracefully.
- [x] Task 4: Preprocessing Pipeline (FR-200)
  - [x] SubTask 4.1: Update `AnomalyDetector` in `src/thermoneural/models/anomaly.py` to use a `sklearn.pipeline.Pipeline`.
  - [x] SubTask 4.2: Add `SimpleImputer(strategy='mean')` and `StandardScaler()` as steps before the `IsolationForest` step.
  - [x] SubTask 4.3: Update tests to verify `NaN` handling and successful preprocessing.

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 and Task 4 can be executed in parallel