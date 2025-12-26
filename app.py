import streamlit as st
from auth import register, login
from styles import apply_style

st.set_page_config(page_title="AI Banking Platform", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- AUTH FLOW ----------
if not st.session_state.logged_in:
    choice = st.radio("", ["Login", "Register"], horizontal=True)

    if choice == "Register":
        register()
    else:
        login()

    st.stop()

# ---------- DASHBOARD ----------
apply_style()

st.sidebar.success(f"Logged in as {st.session_state.user_email}")

st.title("🏦 AI Banking Intelligence Dashboard")
st.write("You are now logged in successfully.")
