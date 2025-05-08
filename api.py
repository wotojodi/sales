import streamlit as st
import time
import json
import os
import pandas as pd
import plotly.express as px
from io import BytesIO
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from Generating_data import create_record

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide", initial_sidebar_state="collapsed")
CSV_PATH = 'AI_Solution_Dataset.csv'
COOKIE_FILE = "session_cookie.json"
SESSION_DURATION = 3600  # 1 hour
VALID_USERNAME = "kwoto"
VALID_PASSWORD = "abc"

# ----------------- SESSION HANDLING -----------------
def load_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            cookie = json.load(f)
            if cookie.get("expiry_time", 0) > time.time():
                return True
    return False

def save_cookie():
    with open(COOKIE_FILE, "w") as f:
        cookie = {
            "authenticated": True,
            "expiry_time": time.time() + SESSION_DURATION
        }
        json.dump(cookie, f)

def clear_cookie():
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)

# ----------------- LOGIN FORM -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = load_cookie()

if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            save_cookie()
            st.success("Login successful! Refreshing...")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# ----------------- AUTO-REFRESH -----------------
count = st_autorefresh(interval=2000, key="data_refresh")

# ----------------- APPEND NEW DATA -----------------
# Only append one record per refresh using session count
if count > 0 and "last_refresh" not in st.session_state:
    new_record = create_record()
    if os.path.exists(CSV_PATH):
        pd.DataFrame([new_record]).to_csv(CSV_PATH, mode='a', header=False, index=False)
    else:
        pd.DataFrame([new_record]).to_csv(CSV_PATH, index=False)
    st.session_state.last_refresh = count

# ----------------- READ DATA -----------------
@st.cache_data(show_spinner=False)
def load_data(path):
    return pd.read_csv(path, on_bad_lines="skip")

df = load_data(CSV_PATH)

# ----------------- NAVIGATION MENU -----------------
selected = option_menu(
    menu_title=None,
    options=["Sales", "Effectiveness", "Analysis", "Logout"],
    icons=[],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
)

st.title("Sales and Marketing Dashboard")

# ----------------- FILTERS -----------------
st.sidebar.header("Filter Options")
country_filter = st.sidebar.multiselect("Select Country", options=df['Country'].unique())
product_filter = st.sidebar.multiselect("Select Product", options=df['Product Type'].unique())
year_filter = st.sidebar.multiselect("Select Year", options=df['Sales Date'].astype(str).str[:4].unique())

filtered_df = df.copy()
if country_filter:
    filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
if product_filter:
    filtered_df = filtered_df[filtered_df['Product Type'].isin(product_filter)]
if year_filter:
    filtered_df = filtered_df[filtered_df['Sales Date'].astype(str).str[:4].isin(year_filter)]

# ----------------- EXPORT CSV -----------------
st.subheader("Export Filtered Data")
towrite = BytesIO()
filtered_df.to_csv(towrite, index=False)
towrite.seek(0)
st.download_button(
    label="Export to CSV",
    data=towrite,
    file_name='AI_Solution_Dataset.csv',
    mime='text/csv'
)

# ----------------- SALES TAB -----------------
if selected == "Sales":
    # All your KPIs and visuals remain the same here...
    st.success("✅ Data is now live and updates every 2 seconds.")
    # [Place all existing KPI and chart code here as-is]

# ----------------- EFFECTIVENESS TAB -----------------
elif selected == "Effectiveness":
    # [Keep your effectiveness metrics and visuals here]

# ----------------- ANALYSIS TAB -----------------
elif selected == "Analysis":
    # [Keep your analysis section here]

# ----------------- LOGOUT -----------------
elif selected == "Logout":
    clear_cookie()
    st.session_state.authenticated = False
    st.success("Logged out.")
    st.experimental_rerun()
