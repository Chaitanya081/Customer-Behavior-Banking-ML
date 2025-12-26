import streamlit as st
import os
import pandas as pd
import numpy as np
from styles import apply_login_style
from auth import register_user, login_user

st.set_page_config(page_title="AI Banking Platform", layout="wide")

# ---------------- SESSION INIT ----------------
if "users" not in st.session_state:
    st.session_state["users"] = {}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

IMAGE_PATH = os.path.join(os.getcwd(), "images", "loginimage.jpg")

# ---------------- LOGIN PAGE ----------------
if not st.session_state["logged_in"]:
    apply_login_style(IMAGE_PATH)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🔐 AI Banking Platform")

    option = st.radio("Select Option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if register_user(email, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("User already exists")

    else:
        if st.button("Login"):
            if login_user(email, password):
                st.session_state["logged_in"] = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD ----------------
else:
    # ========== SIDEBAR ==========
    st.sidebar.markdown("## 🏦 AI Banking")
    st.sidebar.success("Logged in")

    menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "📈 Customer Analysis", "🔮 Risk Prediction", "🚪 Sign Out"]
    )

    # ========== DASHBOARD ==========
    if menu == "📊 Dashboard":
        st.title("🏦 AI Banking Intelligence Dashboard")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", "45,211")
        col2.metric("High Risk Customers", "12%")
        col3.metric("Retention Rate", "88%")

        st.subheader("📊 Customer Overview")
        chart_data = pd.DataFrame({
            "Category": ["Low Risk", "Medium Risk", "High Risk"],
            "Customers": [28000, 12000, 5200]
        })
        st.bar_chart(chart_data.set_index("Category"))

    # ========== CUSTOMER ANALYSIS ==========
    elif menu == "📈 Customer Analysis":
        st.title("📈 Customer Behavior Analysis")

        st.write("Distribution of customer engagement levels")

        engagement = pd.DataFrame({
            "Engagement": ["Low", "Medium", "High"],
            "Count": [15000, 20000, 10211]
        })

        st.bar_chart(engagement.set_index("Engagement"))

        st.write("Insights:")
        st.success("High engagement customers show lower churn risk")

    # ========== RISK PREDICTION ==========
    elif menu == "🔮 Risk Prediction":
        st.title("🔮 Customer Risk Prediction (User Input)")

        st.info("Enter customer details to predict risk")

        age = st.slider("Age", 18, 70, 30)
        balance = st.number_input("Account Balance", value=50000)
        loans = st.selectbox("Has Loan?", ["Yes", "No"])
        calls = st.slider("Marketing Calls", 0, 20, 3)

        if st.button("Predict Risk"):
            score = age * 0.2 + balance * 0.00001 + calls * 0.5
            if loans == "Yes":
                score += 5

            if score < 15:
                st.success("🟢 Low Risk Customer")
            elif score < 30:
                st.warning("🟡 Medium Risk Customer")
            else:
                st.error("🔴 High Risk Customer")

    # ========== SIGN OUT ==========
    elif menu == "🚪 Sign Out":
        st.session_state["logged_in"] = False
        st.success("Signed out successfully")
        st.rerun()
