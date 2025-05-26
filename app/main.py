import streamlit as st
import pandas as pd
from data_provider import fetch_trade_data
from streamlit_autorefresh import st_autorefresh
import re

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# --- Sidebar ---
st.sidebar.title("Settings")
refresh_interval = st.sidebar.slider("Refresh interval (s)", 1, 30, 5)
symbol = st.sidebar.text_input("Symbol (e.g., btcusdt)", value="btcusdt").lower()

# --- Validate symbol input ---
if not symbol or symbol.strip() == "":
    st.error("⚠️ Please enter a valid symbol (e.g., btcusdt).")
    st.stop()

# Validate symbol format (should be like btcusdt, ethusdt, etc.)
if not re.match(r'^[a-z0-9]+(usdt|btc|eth|bnb)$', symbol):
    st.error("⚠️ Invalid symbol format. Please use format like 'btcusdt', 'ethusdt', etc.")
    st.stop()

alert_threshold = st.sidebar.number_input("🔔 Alert if price > $", min_value=0.0, value=0.0, step=10.0)
sound_alert = st.sidebar.checkbox("🔊 Enable Sound Alert")

# --- Dark Mode Toggle ---
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

new_theme = "dark" if dark_mode else "light"
if st.session_state["theme"] != new_theme:
    st.session_state["theme"] = new_theme
    st.rerun()

# Inject dark/light mode via CSS + JS
st.markdown(f"""
    <style>
    /* Light mode styles */
    body {{
        background-color: white;
        color: black;
    }}
    
    /* Dark mode styles */
    body[data-theme="dark"] {{
        background-color: #0e1117;
        color: white;
    }}
    
    /* Style for Streamlit elements */
    .stApp {{
        background-color: {st.session_state["theme"] == "dark" and "#0e1117" or "white"};
        color: {st.session_state["theme"] == "dark" and "white" or "black"};
    }}
    
    /* Style for sidebar */
    .css-1d391kg, .css-1d391kg > div {{
        background-color: {st.session_state["theme"] == "dark" and "#1e2130" or "white"} !important;
        color: {st.session_state["theme"] == "dark" and "white" or "black"};
    }}

    /* Style for sidebar elements */
    .css-1d391kg .stSlider, 
    .css-1d391kg .stTextInput,
    .css-1d391kg .stNumberInput,
    .css-1d391kg .stCheckbox {{
        background-color: {st.session_state["theme"] == "dark" and "#1e2130" or "white"} !important;
        color: {st.session_state["theme"] == "dark" and "white" or "black"} !important;
    }}
    
    /* Style for metric cards */
    .stMetric {{
        background-color: {st.session_state["theme"] == "dark" and "#1e2130" or "white"};
        border: 1px solid {st.session_state["theme"] == "dark" and "#2d3748" or "#e0e0e0"};
        border-radius: 5px;
        padding: 10px;
        color: {st.session_state["theme"] == "dark" and "white" or "black"};
    }}

    /* Style for metric values and labels */
    .stMetric label, .stMetric div {{
        color: {st.session_state["theme"] == "dark" and "white" or "black"} !important;
    }}

    /* Style for titles and text */
    h1, h2, h3, p, .stMarkdown {{
        color: {st.session_state["theme"] == "dark" and "white" or "black"};
    }}

    /* Style for chart text */
    .stChart {{
        color: {st.session_state["theme"] == "dark" and "white" or "black"};
    }}
    </style>
    <script>
        document.body.setAttribute('data-theme', '{st.session_state["theme"]}');
    </script>
""", unsafe_allow_html=True)

# --- Auto-refresh ---
st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# --- Fetch Data with cache ---
@st.cache_data(ttl=refresh_interval)
def get_data(symbol: str):
    return fetch_trade_data(symbol)

try:
    data = get_data(symbol)
    df = pd.DataFrame(data)
except Exception as e:
    error_msg = str(e)
    if "Invalid symbol" in error_msg or "symbol does not exist" in error_msg.lower():
        st.error(f"❌ Invalid trading pair '{symbol.upper()}'. Please check if this trading pair exists on Binance.")
    elif "timeout" in error_msg.lower():
        st.error("❌ Connection timeout. Please check your internet connection and try again.")
    else:
        st.error(f"❌ Failed to fetch data: {error_msg}")
    st.stop()

st.title(f"📊 {symbol.upper()} Live Dashboard (Polling)")

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp").sort_index()
    df["rolling_mean"] = df["price"].rolling("60s").mean()
    df["pct_change"] = df["price"].pct_change() * 100

    last_price = df['price'].iloc[-1]

    # --- Alert Check ---
    if alert_threshold > 0 and last_price > alert_threshold:
        st.error(f"🚨 ALERT: Price crossed ${alert_threshold:,.2f}!")

        if sound_alert:
            st.markdown("""
            <audio autoplay>
                <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="audio/mpeg">
            </audio>
            """, unsafe_allow_html=True)

    # --- Metric cards ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Last Price", f"${last_price:,.2f}")
    col2.metric("1-min Δ%", f"{df['pct_change'].iloc[-1]:.2f}%")
    col3.metric("1-min Volume", f"{df['volume'].tail(60).sum():,.2f}")

    # --- Chart (highlight if above threshold) ---
    chart_df = df[["price", "rolling_mean"]].copy()
    if alert_threshold > 0:
        chart_df["threshold"] = alert_threshold  # constant line for comparison

    st.line_chart(chart_df)
else:
    st.warning("⏳ Waiting for data...")
