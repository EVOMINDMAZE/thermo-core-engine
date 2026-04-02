# Thorough Headed Test Spec

## Why
With the recent additions of physics-informed rules, uncertainty quantification, multi-asset fleet views, and database logging, the UI has become significantly more complex. We need to plan and execute a thorough, visually verifiable ("headed") end-to-end test to debug the application, observe its behavior in real-time, and figure out exactly what is going on if any components (like the new Fleet tabs, Radar charts, or PDF generator) are failing silently.

## What Changes
- Add a new debugging script `scripts/debug_headed_test.py` that uses Playwright in `headless=False` mode.
- The script will deliberately slow down interactions (using `slow_mo` and strategic pauses) so a human can watch the execution step-by-step.
- It will interact with the "Number of Assets" slider to generate multi-asset synthetic data and trigger the "Fleet Overview" tab.
- It will navigate into specific assets, check the "Executive Summary", verify the uncertainty quantification display (e.g., "85% ± X%"), and interact with the "Technical Diagnostics" tab.
- The script will capture and print all browser console errors to the terminal to identify hidden UI or Plotly rendering failures.
- It will take diagnostic screenshots at key failure points.

## Impact
- Affected specs: End-to-End Testing, Debugging
- Affected code: `scripts/debug_headed_test.py` (New)

## ADDED Requirements
### Requirement: Headed E2E Debugging
The system SHALL provide a dedicated, headed E2E script for visual debugging and console error capture.

#### Scenario: Success case
- **WHEN** a developer runs the headed test script
- **THEN** a visible Chromium browser window opens, navigates through the Fleet and Asset views slowly, captures console logs, takes a screenshot of the final state, and successfully closes, allowing the developer to "figure out what's going on."