import streamlit as st
import time
import json
import os

VALID_USERNAME = "kwoto"
VALID_PASSWORD = "abc"

COOKIE_FILE = "session_cookie.json"
SESSION_DURATION = 3600  # 1 hour

st.set_page_config(page_title="Login", layout="centered")

# ---- Load simulated cookie ----
def load_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            cookie = json.load(f)
            if cookie["expiry_time"] > time.time():
                return True
    return False

# ---- Save simulated cookie ----
def save_cookie():
    with open(COOKIE_FILE, "w") as f:
        cookie = {
            "authenticated": True,
            "expiry_time": time.time() + SESSION_DURATION
        }
        json.dump(cookie, f)

# ---- Check previous session ----
if load_cookie():
    st.session_state.authenticated = True
    st.switch_page("pages/api.py")

# ---- Login form ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            save_cookie()
            st.success("Login successful! Redirecting...")
            st.switch_page("pages/api.py")
        else:
            st.error("Invalid credentials")
