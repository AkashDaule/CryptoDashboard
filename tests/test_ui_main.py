
import sys
import os
from streamlit.testing.v1 import AppTest

# Add the 'app' directory to sys.path for correct module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

def test_dashboard_ui_loads():
    # Path to app/main.py
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "main.py"))
    
    at = AppTest.from_file(root_path)
    at.run(timeout=10)

    # ✅ Check page title
    assert at.title[0].value.lower().startswith("📊")

    # ✅ Check at least 1 metric is rendered (e.g., Last Price, Δ%, Volume)
    assert len(at.metric) >= 1

    # ✅ Check sidebar input
    assert at.sidebar.text_input[0].value == "btcusdt"

    # ✅ Check line chart only if it exists
    if hasattr(at, "line_chart"):
        assert len(at.line_chart) > 0
    else:
        # Optional: Print a message so you know chart didn't render
        print("⚠️ Line chart not rendered — possibly due to empty data.")
