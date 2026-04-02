import os

import fitz  # PyMuPDF
from playwright.sync_api import Page


def test_streamlit_e2e(page: Page):
    """
    Automated E2E Test:
    1. Opens Streamlit app.
    2. Generates Synthetic Data.
    3. Runs Analysis.
    4. Downloads the PDF.
    5. Analyzes the text of the PDF to verify expected output.
    """
    # 1. Navigate to the app
    print("Navigating to Streamlit app...")
    page.goto("http://localhost:8501")

    # Wait for the app to load fully
    page.wait_for_selector("text=Thermoneural Engine", timeout=10000)

    # 2. Select Data Source -> Use Synthetic Data
    print("Selecting Synthetic Data...")
    page.click("text=Use Synthetic Data")

    # Click "Generate Synthetic Data" button
    print("Generating Synthetic Data...")
    page.click("button:has-text('Generate Synthetic Data')")

    # Wait for success message
    page.wait_for_selector("text=Synthetic data generated successfully!", timeout=10000)

    # 3. Run Analysis
    print("Running Analysis...")
    page.click("button:has-text('Run Analysis')")

    # Wait for the analysis to finish (the download button appears)
    print("Waiting for Analysis to complete...")
    page.wait_for_selector("button:has-text('Download RCA Report (PDF)')", timeout=30000)

    # 4. Handle Download
    print("Downloading PDF...")
    with page.expect_download() as download_info:
        page.click("button:has-text('Download RCA Report (PDF)')")
    download = download_info.value

    # Save the PDF to a temporary path
    pdf_path = os.path.join(os.getcwd(), "test_report.pdf")
    download.save_as(pdf_path)
    print(f"PDF saved to {pdf_path}")

    # 5. Analyze the PDF text
    print("Analyzing PDF text...")
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        text += doc[page_num].get_text()
    doc.close()

    print("\n--- Extracted PDF Text ---")
    print(text)
    print("--------------------------\n")

    # Assertions to ensure production readiness
    assert "Thermoneural Engine" in text
    assert "Executive Summary" in text
    # PDF text extraction sometimes breaks lines in weird places, so we check case-insensitively
    # or handle newlines if needed, but lowercasing and removing newlines is safer:
    clean_text = text.replace('\n', ' ').lower()

    assert "scroll valve leak" in clean_text, "Did not correctly identify Scroll Valve Leak!"
    assert "confidence score: 85.0%" in clean_text, "Confidence score is incorrect!"
    assert "severity: medium" in clean_text
    assert "likely root cause: seal degradation" in clean_text
    assert "downtime risk: low" in clean_text
    assert "inspect scroll valve seals and plan for replacement" in clean_text
    assert "metrics breakdown" in clean_text
    assert "peak temperature during anomaly" in clean_text
    assert "peak vibration during anomaly" in clean_text
    assert "financial risk assessment" in clean_text
    assert "estimated downtime cost:" in clean_text
    assert "total risk exposure:" in clean_text
    assert "recommended actions" in clean_text
    assert "how to read this chart:" in clean_text

    # Cleanup
    os.remove(pdf_path)
    print("✅ E2E Test Passed Successfully!")
