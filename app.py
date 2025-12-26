import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from auth import login_user, register_user
from models import predict_risk
from styles import load_styles
from utils import get_image_path

st.set_page_config(page_title="AI Banking Platform", layout="wide")
load_styles()

# SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# ---------- LOGIN / REGISTER ----------
if not st.session_state.logged_in:

    st.image(get_image_path("loginimage.jpg"), use_container_width=True)

    st.title("🔐 AI Banking Platform")

    option = st.radio("Select Option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if register_user(email, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("User already exists.")

    if option == "Login":
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.logged_in = True
                st.session_state.user = email
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

# ---------- DASHBOARD ----------
else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    st.title("🏦 AI Banking Intelligence Dashboard")

    df = pd.read_csv("data/bank_marketing.csv")

    # ----- GRAPHS -----
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Subscription Outcome")
        fig, ax = plt.subplots()
        df["y"].value_counts().plot(kind="bar", ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("🥧 Contact Type Distribution")
        fig2, ax2 = plt.subplots()
        df["contact"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
        st.pyplot(fig2)

    # ----- ML PREDICTION -----
    st.subheader("🤖 Risk Prediction (External User)")

    if st.button("Run Risk Prediction"):
        risk = predict_risk(df)
        st.success(f"Predicted Risk Class: {risk}")

    # ----- MANUAL INPUT -----
    st.subheader("📝 Manual Customer Prediction")

    age = st.number_input("Age", 18, 100)
    balance = st.number_input("Balance")
    campaign = st.number_input("Campaign Calls", 1, 50)

    if st.button("Predict Manually"):
        st.info("Manual prediction demo (extendable for real-time use)")
