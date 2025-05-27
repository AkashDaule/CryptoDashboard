import streamlit as st
import pandas as pd
import re
from data_provider import fetch_trade_data
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# --- Sidebar ---
st.sidebar.title("Settings")
refresh_interval = st.sidebar.slider("Refresh interval (s)", 1, 30, 5)
symbol = st.sidebar.text_input("Symbol (e.g., btcusdt)", value="btcusdt").lower()

# --- Symbol Validation ---
if not symbol or not re.match(r'^[a-z0-9]+(usdt|btc|eth|bnb)$', symbol):
    st.error("⚠️ Invalid symbol format. Use like 'btcusdt'.")
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

# --- Inject Dark Mode CSS ---
st.markdown(f"""
    <style>
    body {{
        background-color: {'#0e1117' if dark_mode else 'white'};
        color: {'white' if dark_mode else 'black'};
    }}
    .stApp {{
        background-color: {'#0e1117' if dark_mode else 'white'};
        color: {'white' if dark_mode else 'black'};
    }}
    </style>
    <script>
        document.body.setAttribute('data-theme', '{st.session_state["theme"]}');
    </script>
""", unsafe_allow_html=True)

# --- Auto Refresh ---
st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# --- Data Fetch ---
@st.cache_data(ttl=refresh_interval)
def get_data(symbol: str):
    return fetch_trade_data(symbol)

try:
    data = get_data(symbol)
    df = pd.DataFrame(data)
except Exception as e:
    error_msg = str(e)
    if "Invalid symbol" in error_msg or "symbol does not exist" in error_msg.lower():
        st.error(f"❌ Invalid trading pair '{symbol.upper()}'.")
    else:
        st.error(f"❌ Data fetch failed: {error_msg}")
    st.stop()

st.title(f"📊 {symbol.upper()} Live Dashboard")

# --- Check DataFrame Validity ---
if df.empty or "timestamp" not in df.columns or "price" not in df.columns:
    st.warning("⏳ Waiting for valid data...")
    st.json(data)  # debug output
    st.stop()

# --- Process & Visualize ---
try:
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
    df = df.dropna(subset=["timestamp", "price"])  # remove bad rows
    df = df.set_index("timestamp").sort_index()
    df["rolling_mean"] = df["price"].rolling("60s").mean()
    df["pct_change"] = df["price"].pct_change() * 100

    last_price = df["price"].iloc[-1]

    # --- Alert Logic ---
    if alert_threshold > 0 and last_price > alert_threshold:
        st.error(f"🚨 ALERT: Price crossed ${alert_threshold:,.2f}!")
        if sound_alert:
            st.markdown("""
                <audio autoplay>
                    <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)

    # --- KPI Tiles ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Last Price", f"${last_price:,.2f}")
    col2.metric("1-min Δ%", f"{df['pct_change'].iloc[-1]:.2f}%")
    col3.metric("1-min Volume", f"{df['volume'].tail(60).sum():,.2f}")

    # --- Line Chart ---
    chart_df = df[["price", "rolling_mean"]].copy()
    if alert_threshold > 0:
        chart_df["threshold"] = alert_threshold
    st.line_chart(chart_df)

except Exception as e:
    st.error(f"Chart rendering failed: {e}")
    st.dataframe(df.head())  # fallback debug view
