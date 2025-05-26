import pandas as pd
import numpy as np
import pytest

# Sample function you might want to test (you can adapt these or place in your code base)
def calculate_rolling_mean(df, window='60s'):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp").sort_index()
    df["rolling_mean"] = df["price"].rolling(window).mean()
    return df

def calculate_pct_change(df):
    df["pct_change"] = df["price"].pct_change() * 100
    return df

def calculate_volume_sum(df, window=60):
    # Assuming each row is 1 second apart, sum last `window` volumes
    return df["volume"].tail(window).sum()

# --- Test cases ---

def test_rolling_mean_calculation():
    # Create test data: 3 prices spaced 1 second apart
    data = {
        "timestamp": pd.date_range("2025-01-01 00:00:00", periods=3, freq="s"),
        "price": [10, 20, 30]
    }
    df = pd.DataFrame(data)
    df = calculate_rolling_mean(df, window='3s')
    # Rolling mean at last timestamp = mean of 10,20,30 = 20
    assert np.isclose(df["rolling_mean"].iloc[-1], 20)

def test_pct_change_calculation():
    data = {
        "price": [100, 110, 121]
    }
    df = pd.DataFrame(data)
    df = calculate_pct_change(df)
    # pct_change for second row = (110-100)/100*100 = 10%
    assert np.isclose(df["pct_change"].iloc[1], 10)
    # pct_change for third row = (121-110)/110*100 = 10%
    assert np.isclose(df["pct_change"].iloc[2], 10)

def test_volume_sum_calculation():
    data = {
        "volume": list(range(1, 101))  # volumes from 1 to 100
    }
    df = pd.DataFrame(data)
    volume_sum = calculate_volume_sum(df, window=10)
    # Sum of last 10 volumes = 91+92+...+100 = 955
    assert volume_sum == sum(range(91, 101))

