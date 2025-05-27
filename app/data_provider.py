import requests
import time
import os
import pandas as pd
import streamlit as st

API_URL = "https://api.binance.com/api/v3/trades"
IS_TESTING = bool(os.environ.get("PYTEST_CURRENT_TEST"))

# Cache only when not testing
if not IS_TESTING:
    @st.cache_data(ttl=5)
    def fetch_trade_data(symbol: str, limit: int = 300):
        return _fetch_trade_data(symbol, limit)
else:
    def fetch_trade_data(symbol: str, limit: int = 300):
        return _fetch_trade_data(symbol, limit)

def _fetch_trade_data(symbol: str, limit: int = 300):
    url = f"{API_URL}?symbol={symbol.upper()}&limit={limit}"
    retries = 3
    backoff = 1

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Transform to list of dicts (clean structure)
            formatted = [
                {
                    "timestamp": d["time"],
                    "price": float(d["price"]),
                    "volume": float(d["qty"])
                }
                for d in data
                if "time" in d and "price" in d and "qty" in d
            ]

            return formatted

        except requests.RequestException as e:
            print(f"Fetch error (attempt {attempt + 1}): {e}")
            time.sleep(backoff)
            backoff *= 2

    raise RuntimeError("Failed to fetch trade data after retries.")
