import os
import tempfile
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


def generate_pdf_report(data, analysis, output_path):
    """
    Generate a PDF report from data and analysis results.

    Args:
        data (dict or pd.DataFrame): The raw data to plot.
        analysis (dict): The analysis results.
        output_path (str or Path): The path to save the generated PDF.
    """
    # Create a temporary directory for the plot
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate plot
        df = pd.DataFrame(data)

        # FR-2.2: Two vertically stacked subplots sharing X-axis
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        if 'timestamp' in df.columns and 'temperature' in df.columns:

            # Masks for separating normal vs anomaly points
            normal_mask = ~df['is_anomaly'] if 'is_anomaly' in df.columns else pd.Series(True, index=df.index)
            anomaly_mask = df['is_anomaly'] if 'is_anomaly' in df.columns else pd.Series(False, index=df.index)

            # FR-2.3: Top subplot for Temperature
            ax1.plot(df['timestamp'][normal_mask], df['temperature'][normal_mask],
                     'b-', alpha=0.6, label='Temperature')
            ax1.scatter(df['timestamp'][anomaly_mask], df['temperature'][anomaly_mask],
                       color='red', marker='x', s=100, label='Temp Anomaly')
            ax1.set_ylabel('Temperature (°C)')
            ax1.set_title('Sensor Trends: Temperature')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)

            # FR-2.4: Bottom subplot for Vibration
            if 'vibration' in df.columns:
                ax2.plot(df['timestamp'][normal_mask], df['vibration'][normal_mask],
                         'g-', alpha=0.6, label='Vibration')
                ax2.scatter(df['timestamp'][anomaly_mask], df['vibration'][anomaly_mask],
                           color='darkred', marker='+', s=100, label='Vib Anomaly')
                ax2.set_ylabel('Vibration (mm/s)')
                ax2.set_title('Sensor Trends: Vibration')
                ax2.legend(loc='upper left')
                ax2.grid(True, alpha=0.3)

            ax2.set_xlabel('Timestamp')

            # Format x-axis dates nicely
            plt.gcf().autofmt_xdate()
        else:
            # Fallback plot
            if not df.empty:
                # Exclude timestamp if it exists so it doesn't mess up y-axis scaling
                cols_to_plot = [col for col in df.columns if col not in ['timestamp', 'date', 'is_anomaly']]
                df[cols_to_plot].plot(ax=ax1)
            ax1.set_title('Data Plot')

        plot_path = os.path.join(temp_dir, 'plot.png')
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        # Load template
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('report.html')

        # Get current date for the report header
        current_date = datetime.now().strftime("%B %d, %Y")

        # Render HTML
        html_out = template.render(
            analysis=analysis,
            plot_path=f"file://{os.path.abspath(plot_path)}",
            generation_date=current_date
        )

        # Generate PDF
        HTML(string=html_out).write_pdf(output_path)
