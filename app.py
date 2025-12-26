import streamlit as st
import base64
import pandas as pd
import plotly.express as px

from auth import init_auth, login_user, register_user, logout_user
from models import customer_metrics, bar_chart_data, predict_customer

st.set_page_config(page_title="AI Banking Platform", layout="wide")

# ---------- BACKGROUND IMAGE ----------
def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------- INIT ----------
init_auth()

# ---------- LOGIN PAGE ----------
def login_page():
    set_background("images/loginimage.jpg")

    st.markdown("## 🏦 AI Banking Platform")
    option = st.radio("Select Option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if register_user(email, password):
                st.success("Registered successfully. Please login.")
            else:
                st.error("User already exists")

    if option == "Login":
        if st.button("Login"):
            if login_user(email, password):
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------- DASHBOARD ----------
def dashboard():
    st.sidebar.markdown("### 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.markdown(f"**{st.session_state.current_user}**")

    st.sidebar.markdown("---")
    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customer Prediction", "Analytics"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        logout_user()
        st.rerun()

    metrics = customer_metrics()

    st.title("🏛️ AI Banking Intelligence Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", metrics["total_customers"])
    col2.metric("High Risk", f'{metrics["high_risk"]}%')
    col3.metric("Retention Rate", f'{metrics["retention"]}%')

    if menu == "Dashboard":
        df = bar_chart_data()
        fig = px.bar(df, x="Category", y="Customers", title="Customer Risk Distribution")
        st.plotly_chart(fig, use_container_width=True)

    if menu == "Customer Prediction":
        st.subheader("🔍 Predict Customer Risk")

        age = st.number_input("Age", 18, 100)
        balance = st.number_input("Account Balance")
        campaign = st.number_input("Campaign Contacts", 0, 50)

        if st.button("Predict Risk"):
            result = predict_customer(age, balance, campaign)
            st.success(f"Predicted Risk Level: **{result}**")

    if menu == "Analytics":
        st.subheader("📊 Analytics Overview")
        st.info("Advanced analytics module ready for future expansion")

# ---------- ROUTING ----------
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
