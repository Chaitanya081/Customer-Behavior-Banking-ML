import streamlit as st
import os
import pandas as pd

from auth import login_user, register_user
from styles import apply_login_style
from models import simple_risk_prediction
from utils import show_graphs

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Banking Platform", layout="wide")

IMAGE_PATH = os.path.join("images", "loginimage.jpg")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    apply_login_style(IMAGE_PATH)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("## 🔐 AI Banking Platform")

    option = st.radio("Select Option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if register_user(email, password):
                st.success("Registered successfully! Now login.")
            else:
                st.error("User already exists.")

    if option == "Login":
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- DASHBOARD ----------------
st.sidebar.success(f"Logged in as {st.session_state.user}")

st.title("🏦 AI Banking Intelligence Dashboard")

df = pd.read_csv("data/bank_marketing.csv")

# --------- GRAPHS ----------
fig1, fig2 = show_graphs(df)
st.pyplot(fig1)
st.pyplot(fig2)

# --------- CUSTOM PREDICTION ----------
st.subheader("🔍 Predict Customer Risk")

age = st.number_input("Age", 18, 100)
balance = st.number_input("Account Balance")
duration = st.number_input("Call Duration")

if st.button("Predict Risk"):
    result = simple_risk_prediction(age, balance, duration)
    st.success(f"Predicted Risk Level: **{result}**")
