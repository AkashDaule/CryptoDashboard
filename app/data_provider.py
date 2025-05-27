import requests
import pandas as pd
import streamlit as st
import os

API_URL = "https://api.binance.com/api/v3/ticker/24hr"

IS_TESTING = bool(os.environ.get("PYTEST_CURRENT_TEST"))
print("Running in test mode?", IS_TESTING)

if not IS_TESTING:
    @st.cache_data(ttl=5)
    def fetch_trade_data(symbol: str) -> pd.DataFrame:
        return _fetch_trade_data(symbol)
else:
    def fetch_trade_data(symbol: str) -> pd.DataFrame:
        return _fetch_trade_data(symbol)

def _fetch_trade_data(symbol: str) -> pd.DataFrame:
    url = f"{API_URL}?symbol={symbol.upper()}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame([{
            "price": float(data["lastPrice"]),
            "volume": float(data["volume"]),
            "priceChangePercent": float(data["priceChangePercent"]),
            "timestamp": pd.Timestamp.now()
        }])

        return df

    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch data: {e}")
