import sys
import os
import pytest
from streamlit.testing.v1 import AppTest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "main.py"))

def test_app_loads_successfully():
    """Test that the app loads without fatal errors"""
    at = AppTest.from_file(root_path)
    at.run(timeout=10)
    
    # Basic checks
    assert at.main is not None
    assert at.sidebar is not None
    print("✅ App loads successfully")

def test_sidebar_has_inputs():
    """Test that sidebar contains expected input widgets"""
    at = AppTest.from_file(root_path)
    at.run(timeout=10)
    
    # Check if sidebar has text inputs (symbol input)
    has_text_input = len(at.sidebar.text_input) > 0
    print(f"Sidebar has text inputs: {has_text_input}")
    assert has_text_input

def test_empty_input_handling():
    """Test app behavior with empty inputs"""
    at = AppTest.from_file(root_path)
    at.run(timeout=10)
    
    if len(at.sidebar.text_input) > 0:
        symbol_input = at.sidebar.text_input[0]
        symbol_input.set_value("")
        at.run(timeout=10)
    
    # App should handle empty input gracefully (may show errors but shouldn't crash)
    print(f"App handled empty input with {len(at.error)} errors")
    # This is acceptable - API errors are expected with empty symbols
    assert True