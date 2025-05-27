import requests
import time
import pandas as pd
import streamlit as st
import os

API_URL = "https://api.binance.com/api/v3/trades"

# Check if we are running inside pytest (used to disable caching)
IS_TESTING = bool(os.environ.get("PYTEST_CURRENT_TEST"))
print("Running in test mode?", IS_TESTING)  # Debug line to confirm testing mode

# Use cache only when not testing
if not IS_TESTING:
    @st.cache_data(ttl=5)
    def fetch_trade_data(symbol: str, limit: int = 300) -> pd.DataFrame:
        return _fetch_trade_data(symbol, limit)
else:
    def fetch_trade_data(symbol: str, limit: int = 300) -> pd.DataFrame:
        return _fetch_trade_data(symbol, limit)

def _fetch_trade_data(symbol: str, limit: int = 300) -> pd.DataFrame:
    url = f"{API_URL}?symbol={symbol.upper()}&limit={limit}"
    retries = 3
    backoff = 1

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Create DataFrame
            df = pd.DataFrame(data)
            df = df.rename(columns={
                "price": "price",
                "qty": "volume",
                "time": "timestamp"
            })[["price", "volume", "timestamp"]]

            df["price"] = df["price"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Sort by timestamp ascending
            df = df.sort_values("timestamp").reset_index(drop=True)

            # Limit rows to 300 max
            if len(df) > 300:
                df = df.tail(300).reset_index(drop=True)

            return df

        except requests.RequestException as e:
            print(f"Error fetching data (attempt {attempt + 1}): {e}")
            time.sleep(backoff)
            backoff *= 2

    raise RuntimeError("Failed to fetch trade data after multiple retries.")
