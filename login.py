import streamlit as st

# Dummy credentials for demo purposes
VALID_USERNAME = "kwoto"
VALID_PASSWORD = "abc"

st.set_page_config(page_title="Login", layout="centered")

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        # Set a session state variable to mark the user as authenticated
        st.session_state.authenticated = True
        # Redirect to dashboard by switching page (Streamlit >= 1.27)
        st.switch_page("pages/dsh.py")
    else:
        st.error("Invalid username or password")

# If already logged in, skip login page
if st.session_state.get("authenticated"):
    st.switch_page("pages/dsh.py")