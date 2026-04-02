# Tasks
- [x] Task 1: Prevent `MessageSizeError` on Large Data
  - [x] SubTask 1.1: Update `.streamlit/config.toml` to explicitly include `maxMessageSize = 1024` under the `[server]` section.
  - [x] SubTask 1.2: Update `app.py` to only show `st.dataframe(df.head(1000))` in the "Raw Data Preview" expander. Add a caption indicating it's a preview of the first 1000 rows.
  - [x] SubTask 1.3: Update the "Detailed Sensor Trends" plotting logic in `app.py` to safely downsample the `df_results` base line chart if `len(df_results) > 10000` (e.g., `df_plot = df_results.iloc[::N]`), while keeping all `anomalies` points explicitly drawn so no anomalies are missed in the visualization.
  - [x] SubTask 1.4: Do the same downsampling for the "Isolation Forest Diagnostics" scatter plot.

- [x] Task 2: Fix `KeyError` on Missing Sensors
  - [x] SubTask 2.1: Update `render_tech_diag` in `app.py` to dynamically find which of the expected sensors (`temperature`, `pressure`, `vibration`, `current`) exist in `anomalies.columns`.
  - [x] SubTask 2.2: Build the "Peak Values" table dynamically. Only include rows for sensors that exist.
  - [x] SubTask 2.3: Build the Radar Chart categories and values dynamically. If a sensor is missing, do not include it in the radar axes.
  - [x] SubTask 2.4: Build the "Detailed Sensor Trends" subplots dynamically, ensuring the number of rows (`make_subplots`) matches the number of available sensors.