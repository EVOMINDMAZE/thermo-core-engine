import os
import tempfile

import pandas as pd
import streamlit as st

from thermoneural.data.synthetic import generate_sensor_data
from thermoneural.models.anomaly import AnomalyDetector, group_anomalies_into_incidents
from thermoneural.reports.generator import generate_pdf_report
from thermoneural.rules.expert_system import analyze_root_cause
from thermoneural.storage.db import save_run
from thermoneural.utils.logger import get_logger

logger = get_logger(__name__)

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def main():
    logger.info("Starting Thermoneural Engine app")
    st.set_page_config(page_title="Thermoneural Engine", layout="wide", page_icon="🧊")
    st.title("🧊 Thermoneural Engine")
    st.markdown("### Cryo System Diagnostics & Root-Cause Analysis")
    
    st.markdown("""
    **Transform raw sensor logs into actionable maintenance decisions.**  
    Upload your industrial cryogenic sensor logs (e.g., the *MetroPT-3* dataset) or use our synthetic sample data. 
    Our engine runs an AI-powered anomaly detection pipeline to detect structural faults and maps them to specific failure modes using domain-encoded physics rules.
    """)

    # Sidebar
    st.sidebar.header("Data Input")
    data_source = st.sidebar.radio("Select Data Source", ["Use Synthetic Data", "Upload CSV"])

    df = None
    if data_source == "Use Synthetic Data":
        days = st.sidebar.slider("Days of Data", 7, 90, 30)
        num_assets = st.sidebar.slider("Number of Assets", 1, 5, 1)
        if st.sidebar.button("Generate Synthetic Data"):
            logger.info(f"Generating synthetic data for {days} days and {num_assets} assets")
            df = generate_sensor_data(days=days, n_assets=num_assets)
            st.session_state['df'] = df
            st.session_state['run_analysis'] = False
            if 'results_by_asset' in st.session_state:
                del st.session_state['results_by_asset']
            logger.info("Synthetic data generated successfully")
            st.success("Synthetic data generated successfully!")
    else:
        uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            logger.info(f"User uploaded CSV file: {uploaded_file.name}")
            
            # Read CSV
            try:
                raw_df = load_csv(uploaded_file)
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
                raw_df = None

            if raw_df is not None:
                st.sidebar.subheader("Column Mapping")
                st.sidebar.caption("Map your dataset columns to the engine's expected sensors.")
                
                columns = [""] + list(raw_df.columns)
                
                # Auto-detect common MetroPT-3 and generic names
                def guess_col(possible_names):
                    for col in raw_df.columns:
                        col_lower = col.lower()
                        if any(n.lower() in col_lower for n in possible_names):
                            return col
                    return ""

                time_guess = guess_col(['timestamp', 'time', 'date', 'datetime'])
                temp_guess = guess_col(['temperature', 'temp', 'oil temperature', 'oil temperature (ºc)'])
                pres_guess = guess_col(['pressure', 'tp2', 'tp2 (bar)', 'tp3', 'h1'])
                vib_guess = guess_col(['vibration', 'vib'])
                curr_guess = guess_col(['current', 'motor current', 'motor current (a)'])
                asset_guess = guess_col(['asset', 'asset_id', 'machine', 'machine_id'])

                # UI Selectboxes for mapping
                time_col = st.sidebar.selectbox("Time Column (Required)", columns, index=columns.index(time_guess) if time_guess in columns else 0)
                temp_col = st.sidebar.selectbox("Temperature", columns, index=columns.index(temp_guess) if temp_guess in columns else 0)
                pres_col = st.sidebar.selectbox("Pressure", columns, index=columns.index(pres_guess) if pres_guess in columns else 0)
                vib_col = st.sidebar.selectbox("Vibration", columns, index=columns.index(vib_guess) if vib_guess in columns else 0)
                curr_col = st.sidebar.selectbox("Current", columns, index=columns.index(curr_guess) if curr_guess in columns else 0)
                asset_col = st.sidebar.selectbox("Asset ID (Optional)", columns, index=columns.index(asset_guess) if asset_guess in columns else 0)

                if st.sidebar.button("Apply Mapping & Validate"):
                    mapped_df = raw_df.copy()
                    
                    rename_dict = {}
                    if time_col: rename_dict[time_col] = 'timestamp'
                    if temp_col: rename_dict[temp_col] = 'temperature'
                    if pres_col: rename_dict[pres_col] = 'pressure'
                    if vib_col: rename_dict[vib_col] = 'vibration'
                    if curr_col: rename_dict[curr_col] = 'current'
                    if asset_col: rename_dict[asset_col] = 'asset_id'
                    
                    mapped_df = mapped_df.rename(columns=rename_dict)
                    
                    from thermoneural.data.validation import validate_sensor_data
                    is_valid, error_msg, validated_df = validate_sensor_data(mapped_df)

                    if not is_valid:
                        logger.warning(f"Data validation failed: {error_msg}")
                        st.sidebar.error(error_msg)
                    else:
                        st.session_state['df'] = validated_df
                        st.session_state['run_analysis'] = False
                        if 'results_by_asset' in st.session_state:
                            del st.session_state['results_by_asset']
                        logger.info("CSV data mapped and validated successfully")
                        st.sidebar.success("Data loaded successfully!")

    if 'df' in st.session_state:
        df = st.session_state['df']
        with st.expander(f"Raw Data Preview ({len(df)} rows)"):
            st.dataframe(df.head(1000))

        if st.button("Run Analysis"):
            st.session_state['run_analysis'] = True
            if 'results_by_asset' in st.session_state:
                del st.session_state['results_by_asset']

        if st.session_state.get('run_analysis', False):
            if 'results_by_asset' not in st.session_state:
                logger.info("Run Analysis triggered. Starting pipeline.")
                with st.spinner("Running Anomaly Detection..."):
                    results_by_asset = {}

                    if 'asset_id' not in df.columns:
                        df['asset_id'] = 'Asset-1'
                    assets = df['asset_id'].unique()

                    detector = AnomalyDetector()
                    features = [col for col in ['temperature', 'pressure', 'vibration', 'current'] if col in df.columns]
                    logger.info(f"Running anomaly detection with features: {features}")

                    for asset in assets:
                        asset_df = df[df['asset_id'] == asset].copy()
                        df_results = detector.fit_predict(asset_df, features=features)
                        incidents = group_anomalies_into_incidents(df_results)
                        anomalies = df_results[df_results['is_anomaly']]

                        if not anomalies.empty:
                            analysis = analyze_root_cause(anomalies)
                            if 'anomaly_score_std' in anomalies.columns:
                                avg_std = anomalies['anomaly_score_std'].mean()
                                analysis['confidence_std'] = (0.0 if pd.isna(avg_std) else avg_std * 100)
                            else:
                                analysis['confidence_std'] = 0.0
                        else:
                            analysis = {
                                "failure_mode": "Normal Operation",
                                "confidence": 100.0,
                                "confidence_std": 0.0,
                                "severity": "Normal",
                                "likely_root_cause": "N/A",
                                "downtime_risk": "None",
                                "etf": "N/A",
                                "actions": "Continue normal operations.",
                                "peak_temp": "N/A",
                                "peak_vib": "N/A",
                                "downtime_cost": "$0",
                                "repair_cost": "$0",
                                "total_risk": "$0"
                            }

                        save_run(analysis)
                        results_by_asset[asset] = {
                            'df_results': df_results,
                            'anomalies': anomalies,
                            'analysis': analysis,
                            'incidents': incidents
                        }

                    st.session_state['results_by_asset'] = results_by_asset

            results_by_asset = st.session_state['results_by_asset']
            assets = list(results_by_asset.keys())

            def render_fleet_overview():
                st.write("### Fleet Health Summary")
                
                # Compute KPIs
                total_assets = len(results_by_asset)
                critical_assets = sum(1 for res in results_by_asset.values() if res['analysis'].get("severity") == "Critical")
                high_assets = sum(1 for res in results_by_asset.values() if res['analysis'].get("severity") == "High")
                
                total_risk_val = 0
                for res in results_by_asset.values():
                    risk_str = res['analysis'].get("total_risk", "$0").replace('$', '').replace(',', '')
                    try:
                        total_risk_val += float(risk_str)
                    except ValueError:
                        pass
                
                # Display top-level metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Assets Monitored", total_assets)
                col2.metric("Critical Alerts", critical_assets, delta=f"{critical_assets} Action Required" if critical_assets > 0 else None, delta_color="inverse")
                col3.metric("High Alerts", high_assets)
                col4.metric("Total Fleet Risk Exposure", f"${total_risk_val:,.0f}")
                
                st.divider()
                
                fleet_data = []
                for asset, res in results_by_asset.items():
                    analysis = res['analysis']
                    
                    risk_str = analysis.get("total_risk", "$0").replace('$', '').replace(',', '')
                    try:
                        risk_val = float(risk_str)
                    except ValueError:
                        risk_val = 0.0
                        
                    sev = analysis.get("severity", "Normal")
                    sev_icon = {"Critical": "🔴 Critical", "High": "🟠 High", "Medium": "🟡 Medium", "Low": "🔵 Low", "Normal": "🟢 Normal"}.get(sev, sev)
                    
                    fleet_data.append({
                        "Asset ID": asset,
                        "Status": sev_icon,
                        "Failure Mode": analysis.get("failure_mode", "N/A"),
                        "Downtime Risk": analysis.get("downtime_risk", "N/A"),
                        "Total Risk": risk_val,
                        "Severity_Raw": sev
                    })
                fleet_df = pd.DataFrame(fleet_data)

                # Sort by risk (Severity)
                severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Normal": 4}
                fleet_df['sev_rank'] = fleet_df['Severity_Raw'].map(severity_order).fillna(5)
                fleet_df = fleet_df.sort_values(['sev_rank', 'Total Risk'], ascending=[True, False]).drop(columns=['sev_rank']).reset_index(drop=True)
                
                # Layout for charts and table
                fleet_col1, fleet_col2 = st.columns([2, 1])

                with fleet_col1:
                    st.write("#### Asset Status Details")
                    st.dataframe(
                        fleet_df.drop(columns=['Severity_Raw']), 
                        use_container_width=True, 
                        hide_index=True,
                        column_config={
                            "Asset ID": st.column_config.TextColumn("Asset ID", width="medium"),
                            "Status": st.column_config.TextColumn("Status", width="medium"),
                            "Failure Mode": st.column_config.TextColumn("Failure Mode", width="large"),
                            "Downtime Risk": st.column_config.TextColumn("Downtime Risk", width="medium"),
                            "Total Risk": st.column_config.NumberColumn("Total Risk", format="$%d", width="medium")
                        }
                    )

                with fleet_col2:
                    st.write("#### Severity Distribution")
                    try:
                        import plotly.express as px
                        sev_counts = fleet_df['Severity_Raw'].value_counts().reset_index()
                        sev_counts.columns = ['Severity_Raw', 'Count']
                        
                        color_map = {
                            "Normal": "#00CC96",
                            "Low": "#636EFA",
                            "Medium": "#FECB52",
                            "High": "#FFA15A",
                            "Critical": "#EF553B"
                        }
                        
                        fig = px.pie(sev_counts, values='Count', names='Severity_Raw', hole=0.4, 
                                     color='Severity_Raw', color_discrete_map=color_map)
                        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=False)
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.write("Distribution chart unavailable.")

            def render_asset_details(selected_asset, use_tabs=True):
                asset_data = results_by_asset[selected_asset]
                df_results = asset_data['df_results']
                anomalies = asset_data['anomalies']
                analysis = asset_data['analysis']
                incidents = asset_data['incidents']

                if use_tabs:
                    t1, t2 = st.tabs(["Executive Summary", "Technical Diagnostics"])
                    with t1:
                        render_exec_summary(analysis, df_results)
                    with t2:
                        render_tech_diag(df_results, anomalies)
                else:
                    view_type = st.radio(f"Select View for {selected_asset}", ["Executive Summary", "Technical Diagnostics"], horizontal=True, key=f"view_{selected_asset}")
                    if view_type == "Executive Summary":
                        render_exec_summary(analysis, df_results)
                    else:
                        render_tech_diag(df_results, anomalies)

            def render_exec_summary(analysis, df_results):
                st.write("### Analysis Results")

                severity = analysis.get("severity", "Normal")
                color_mapping = {
                    "Normal": "green",
                    "Low": "blue",
                    "Medium": "yellow",
                    "High": "orange",
                    "Critical": "red"
                }
                sev_color = color_mapping.get(severity, "gray")

                st.markdown(f"""
                <div style="border: 2px solid {sev_color}; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; color: {sev_color};">Top Summary Block</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; font-size: 16px;">
                        <div style="flex: 1 1 30%;">
                            <strong>Failure Mode:</strong><br>
                            {analysis.get('failure_mode', 'N/A')}
                        </div>
                        <div style="flex: 1 1 30%;">
                            <strong>Confidence:</strong><br>
                            {analysis.get('confidence', 'N/A')}% &plusmn; {analysis.get('confidence_std', 0.0):.1f}%
                        </div>
                        <div style="flex: 1 1 30%;">
                            <strong>Severity:</strong><br>
                            <span style="color: {sev_color}; font-weight: bold;">{severity}</span>
                        </div>
                        <div style="flex: 1 1 30%;">
                            <strong>Downtime Risk:</strong><br>
                            {analysis.get('downtime_risk', 'N/A')}
                        </div>
                        <div style="flex: 1 1 100%;">
                            <strong>Likely Root Cause:</strong><br>
                            {analysis.get('likely_root_cause', 'N/A')}
                        </div>
                        <div style="flex: 1 1 100%;">
                            <strong>Recommended Action:</strong><br>
                            {analysis.get('actions', 'N/A')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 5. Report Generation
                asset_id = df_results['asset_id'].iloc[0] if 'asset_id' in df_results.columns else "Asset"
                report_key = f"pdf_bytes_{asset_id}"
                
                if report_key not in st.session_state:
                    if st.button(f"Generate PDF Report for {asset_id}"):
                        with st.spinner("Generating PDF Report..."):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                                pdf_path = tmp_pdf.name

                            generate_pdf_report(df_results, analysis, pdf_path)

                            with open(pdf_path, "rb") as pdf_file:
                                st.session_state[report_key] = pdf_file.read()

                            # Cleanup
                            try:
                                os.unlink(pdf_path)
                            except Exception:
                                pass
                            st.rerun()
                else:
                    st.download_button(
                        label="📄 Download RCA Report (PDF)",
                        data=st.session_state[report_key],
                        file_name=f"Thermoneural_RCA_{asset_id}.pdf",
                        mime="application/pdf"
                    )

            def render_tech_diag(df_results, anomalies):
                st.write("### Technical Diagnostics & Insights")

                # Dynamically determine available sensors
                all_possible_sensors = {
                    'temperature': {'name': 'Temperature', 'unit': '°C', 'color': 'blue'},
                    'pressure': {'name': 'Pressure', 'unit': 'psi', 'color': 'orange'},
                    'vibration': {'name': 'Vibration', 'unit': 'mm/s', 'color': 'green'},
                    'current': {'name': 'Current', 'unit': 'A', 'color': 'purple'}
                }
                
                available_sensors = [s for s in all_possible_sensors.keys() if s in df_results.columns]

                if not available_sensors:
                    st.warning("No sensor data available for diagnostics.")
                    return

                # Row 1: Summary Table and Radar Chart
                diag_col1, diag_col2 = st.columns([1, 1])

                with diag_col1:
                    st.write("#### Peak Values (Anomaly Window)")
                    if not anomalies.empty:
                        peak_sensors = []
                        peak_values = []
                        for s in available_sensors:
                            peak_sensors.append(all_possible_sensors[s]['name'])
                            peak_values.append(f"{anomalies[s].max():.2f} {all_possible_sensors[s]['unit']}")
                        
                        peak_df = pd.DataFrame({
                            "Sensor": peak_sensors,
                            "Peak Value": peak_values
                        })
                        st.table(peak_df)
                    else:
                        st.write("No anomalies detected.")

                with diag_col2:
                    st.write("#### Anomaly Signature (Radar)")
                    try:
                        import plotly.graph_objects as go
                        if not anomalies.empty:
                            # Calculate deviation from normal (simple normalized radar)
                            normal_df = df_results[~df_results['is_anomaly']]
                            categories = [all_possible_sensors[s]['name'] for s in available_sensors]

                            # Use max anomalous values normalized by normal mean
                            values = []
                            for s in available_sensors:
                                mean_val = normal_df[s].mean()
                                if mean_val != 0 and pd.notnull(mean_val):
                                    val = anomalies[s].max() / mean_val
                                else:
                                    val = 1
                                values.append(val)

                            fig_radar = go.Figure()
                            fig_radar.add_trace(go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill='toself',
                                name='Anomaly Signature',
                                line=dict(color='#ff4b4b'), # Match Streamlit/Anomaly red
                                fillcolor='rgba(255, 75, 75, 0.3)'
                            ))
                            fig_radar.update_layout(
                                polar=dict(
                                    radialaxis=dict(visible=True, range=[0, max(values) * 1.2 if values else 1]),
                                    bgcolor='rgba(0,0,0,0)' # Make radar background transparent
                                ),
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                showlegend=False,
                                height=350,
                                margin=dict(l=40, r=40, t=40, b=40)
                            )
                            st.plotly_chart(fig_radar, use_container_width=True)
                        else:
                            st.write("No signature available.")
                    except Exception as e:
                        st.error(f"Radar chart error: {e}")

                # Row 2: Detailed Sensor Trends (Subplots)
                st.write("### Detailed Sensor Trends")

                try:
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots

                    num_sensors = len(available_sensors)
                    subplot_titles = [f"{all_possible_sensors[s]['name']} ({all_possible_sensors[s]['unit']})" for s in available_sensors]

                    fig = make_subplots(rows=num_sensors, cols=1, shared_xaxes=True,
                                        subplot_titles=subplot_titles,
                                        vertical_spacing=0.05)

                    if len(df_results) > 10000:
                        step = len(df_results) // 10000 + 1
                        df_base = df_results.iloc[::step]
                    else:
                        df_base = df_results

                    for idx, s in enumerate(available_sensors):
                        row_idx = idx + 1
                        color = all_possible_sensors[s]['color']
                        
                        # Base line
                        fig.add_trace(go.Scattergl(x=df_base['timestamp'], y=df_base[s],
                                                 mode='lines', name=all_possible_sensors[s]['name'],
                                                 line=dict(color=color, width=1), opacity=0.7),
                                      row=row_idx, col=1)

                        # Anomalies overlay
                        if not anomalies.empty:
                            fig.add_trace(go.Scattergl(x=anomalies['timestamp'], y=anomalies[s],
                                                     mode='markers', name=f"{all_possible_sensors[s]['name']} Anomaly",
                                                     marker=dict(color='red', size=6, symbol='x')),
                                          row=row_idx, col=1)

                    fig.update_layout(height=200 * num_sensors + 100, title_text="Multi-Sensor Anomaly Analysis", showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Visualization error: {e}")
                    features = [col for col in ['temperature', 'pressure', 'vibration', 'current'] if col in df_results.columns]
                    st.line_chart(df_results.set_index('timestamp')[features])

                # Plot anomalies score
                st.write("### Isolation Forest Diagnostics")
                try:
                    import plotly.express as px
                    if len(df_results) > 10000:
                        step = len(df_results) // 10000 + 1
                        df_normal = df_results[~df_results['is_anomaly']].iloc[::step]
                        df_anomalies = df_results[df_results['is_anomaly']]
                        df_scatter = pd.concat([df_normal, df_anomalies]).sort_index()
                    else:
                        df_scatter = df_results
                        
                    fig2 = px.scatter(df_scatter, x='timestamp', y='anomaly_score', color='is_anomaly',
                                     color_discrete_map={True: 'red', False: 'blue'},
                                     labels={'anomaly_score': 'Decision Score', 'is_anomaly': 'Flagged'},
                                     title='Model Decision Function Scores',
                                     render_mode='webgl')
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception:
                    st.write("Decision score visualization unavailable.")

            if len(assets) > 1:
                main_tabs = st.tabs(["Fleet Overview", "Asset Details"])
                with main_tabs[0]:
                    render_fleet_overview()
                with main_tabs[1]:
                    selected_asset = st.selectbox("Select Asset", assets)
                    render_asset_details(selected_asset, use_tabs=False)
            else:
                render_asset_details(assets[0], use_tabs=True)

if __name__ == "__main__":
    main()
