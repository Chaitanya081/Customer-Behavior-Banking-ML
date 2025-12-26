import streamlit as st
import pandas as pd
import plotly.express as px
import os

from auth import register_user, login_user
from models import risk_prediction

st.set_page_config(layout="wide", page_title="AI Banking Platform")

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- IMAGE ----------
IMAGE_PATH = "images/loginimage.jpg"

def show_login_image():
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, use_container_width=True)
    else:
        st.warning("Login image not found")

# ---------- LOGIN PAGE ----------
def login_page():
    show_login_image()

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
                st.session_state.logged_in = True
                st.session_state.user = email
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

# ---------- DASHBOARD ----------
def dashboard():
    st.sidebar.markdown("## 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.user)

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "Prediction", "Analytics"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # ---------- SAMPLE DATA ----------
    data = pd.DataFrame({
        "age": [25, 45, 35, 50, 28],
        "balance": [5000, -200, 3000, -1500, 7000]
    })

    # ---------- DASHBOARD ----------
    if page == "Dashboard":
        st.markdown("# 🏦 AI Banking Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Customers", "45,211")
        c2.metric("High Risk", "12%")
        c3.metric("Retention Rate", "88%")

        fig = px.bar(
            x=["Low Risk", "High Risk"],
            y=[80, 20],
            title="Customer Risk Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- ADD CUSTOMER ----------
    if page == "Add Customer":
        st.markdown("## ➕ Add New Customer")

        age = st.number_input("Age", 18, 100)
        balance = st.number_input("Balance")

        if st.button("Add Customer"):
            st.success(f"Customer Added | Age: {age}, Balance: {balance}")

    # ---------- PREDICTION ----------
    if page == "Prediction":
        st.markdown("## 🔮 Risk Prediction")

        result = risk_prediction(data)
        st.dataframe(result)

    # ---------- ANALYTICS ----------
    if page == "Analytics":
        st.markdown("## 📊 Analytics Overview")

        fig = px.pie(
            names=["Low Risk", "High Risk"],
            values=[80, 20],
            title="Risk Split"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------- ROUTER ----------
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
