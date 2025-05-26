import sys
import os
import pytest
from unittest.mock import patch, Mock
import pandas as pd

# Add the root folder to sys.path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data_provider import fetch_trade_data
import requests

# Sample JSON response to mock Binance API data
sample_api_response = [
    {"price": "30000.5", "qty": "0.01", "time": 1685000000000},
    {"price": "30001.0", "qty": "0.02", "time": 1685000001000},
    {"price": "30002.5", "qty": "0.015", "time": 1685000002000},
]

def mocked_requests_get_success(*args, **kwargs):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = sample_api_response
    return mock_resp

def mocked_requests_get_fail(*args, **kwargs):
    raise requests.RequestException("API failure")

@patch('requests.get', side_effect=mocked_requests_get_success)
def test_fetch_trade_data_success(mock_get):
    df = fetch_trade_data("btcusdt", limit=3)
    assert list(df.columns) == ["price", "volume", "timestamp"]
    assert len(df) == 3
    assert pd.api.types.is_float_dtype(df["price"])
    assert pd.api.types.is_float_dtype(df["volume"])
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert df["timestamp"].is_monotonic_increasing

@patch('requests.get', side_effect=mocked_requests_get_fail)
def test_fetch_trade_data_retries_and_fails(mock_get):
    with pytest.raises(RuntimeError):
        fetch_trade_data("btcusdt", limit=3)
    assert mock_get.call_count == 3

@patch('requests.get', side_effect=mocked_requests_get_success)
def test_fetch_trade_data_limits_rows(mock_get):
    big_response = [{"price": "30000", "qty": "0.01", "time": 1685000000000 + i*1000} for i in range(350)]
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = big_response

    with patch('requests.get', return_value=mock_resp):
        df = fetch_trade_data("btcusdt", limit=350)
        assert len(df) == 300
