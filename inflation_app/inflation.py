import streamlit as st
import pandas as pd
import requests
from dateutil import parser
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Mexico Inflation Dashboard", layout="wide")
API_KEY = "e7615df4090e42d:2r2lod3bm0s0p9k"
API_URL = (
    f"https://api.tradingeconomics.com/historical/country/mexico/"
    f"indicator/inflation%20rate?c={API_KEY}"
)

# --- PAGE HEADER ---
st.markdown("# Mexico Inflation Rate Dashboard")
st.markdown("Tracking Mexico's annual inflation rate over time (YoY). Data sourced from [Trading Economics](https://tradingeconomics.com/mexico/inflation-cpi).")

# --- DATA FETCHING ---
@st.cache_data(show_spinner=True)
def fetch_data():
    resp = requests.get(API_URL)
    if resp.status_code != 200:
        st.error(f"Failed to fetch data. Status code: {resp.status_code}")
        return None
    try:
        raw = resp.json()
        df = pd.DataFrame(raw)
        if df.empty or "DateTime" not in df.columns or "Value" not in df.columns:
            return None
        df["DateTime"] = df["DateTime"].apply(parser.isoparse).apply(lambda dt: dt.replace(tzinfo=None))
        df = df.sort_values("DateTime")
        
        # --- FILTER OUT CURRENT MONTH (incomplete data) ---
        today = datetime.today()
        df = df[df["DateTime"] < datetime(today.year, today.month, 1)]

        return df
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

df = fetch_data()

if df is None:
    st.warning("No data available to display at this time.")
    st.stop()

# --- LATEST VALUE & DATE ---
latest_row = df.iloc[-1]
latest_value = latest_row["Value"]
latest_date = latest_row["DateTime"].strftime("%b %Y")

# --- LAYOUT ---
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Inflation Rate Trend")
    st.line_chart(df.set_index("DateTime")["Value"], use_container_width=True)

    st.markdown(
        f"""
        <div style="margin-top: 10px; font-size: 18px;">
            <b>Latest Data:</b><br>
            Inflation Rate (YoY): <span style="color:#d62728;"><b>{latest_value:.2f}%</b></span><br>
            As of: <b>{latest_date}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with right_col:
    st.subheader("Data Table")
    table_df = df[["DateTime", "Value"]].copy()
    table_df.rename(columns={"DateTime": "Date", "Value": "Inflation Rate (%)"}, inplace=True)
    table_df["Date"] = table_df["Date"].dt.strftime("%b %Y")
    st.dataframe(table_df[::-1], use_container_width=True, height=500)  # show newest at top