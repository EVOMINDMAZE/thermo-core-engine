import os
import sys
from playwright.sync_api import sync_playwright

def run_debug_test():
    with sync_playwright() as p:
        print("Launching Chromium browser (headed)...")
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        
        # Create a new browser context and page
        context = browser.new_context()
        page = context.new_page()
        
        # Add a console listener to print browser console messages
        page.on("console", lambda msg: print(f"Browser console [{msg.type}]: {msg.text}"))
        
        # Navigate to the Streamlit app
        url = "http://localhost:8501"
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Wait for the app to load fully
        page.wait_for_selector("text=Thermoneural Engine", timeout=15000)
        print("App loaded successfully.")
        
        # Set 2 assets using the slider
        print("Setting 'Number of Assets' to 2...")
        # Find the slider container for 'Number of Assets' and focus its slider thumb
        slider = page.locator("[data-testid='stSlider']").filter(has_text="Number of Assets").locator("[role='slider']")
        slider.focus()
        # Streamlit sliders usually start at 1, pressing ArrowRight increases it to 2
        page.keyboard.press("ArrowRight")
        
        # Generate data
        print("Clicking 'Generate Synthetic Data'...")
        page.get_by_role("button", name="Generate Synthetic Data").click()
        
        # Wait for success message
        page.wait_for_selector("text=Synthetic data generated successfully!", timeout=15000)
        print("Data generated successfully.")
        
        # Take a screenshot after generating data
        os.makedirs("screenshots", exist_ok=True)
        page.screenshot(path="screenshots/after_data_generation.png")
        print("Screenshot saved: screenshots/after_data_generation.png")
        
        # Run analysis
        print("Clicking 'Run Analysis'...")
        page.get_by_role("button", name="Run Analysis").click()
        
        # Wait for the analysis to finish (Fleet Overview tab appears)
        print("Waiting for Analysis to complete...")
        page.wait_for_selector("text=Fleet Overview", timeout=45000)
        print("Analysis completed.")
        
        page.screenshot(path="screenshots/after_analysis.png")
        print("Screenshot saved: screenshots/after_analysis.png")
        
        # Switch to Asset Details tab
        print("Switching to 'Asset Details' tab...")
        page.get_by_role("tab", name="Asset Details").click()
        
        # Select Asset-1 (ensure it is selected in the selectbox)
        print("Selecting 'Asset-1'...")
        selectbox_container = page.locator("[data-testid='stSelectbox']").filter(has_text="Select Asset")
        selectbox_container.click()
        
        # Click the dropdown option for Asset-1
        page.locator("li[role='option']").filter(has_text="Asset-1").click()
        
        # Wait a moment for the UI to update
        page.wait_for_timeout(2000)
        
        # Take final screenshot
        print("Taking final screenshot of Asset-1 details...")
        page.screenshot(path="screenshots/final_asset1_details.png")
        print("Screenshot saved: screenshots/final_asset1_details.png")
        
        print("Test completed successfully.")
        browser.close()

if __name__ == "__main__":
    run_debug_test()
