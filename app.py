import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Banking Platform",
    page_icon="🏦",
    layout="wide"
)

# ---------------- SESSION STATE INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {"admin@gmail.com": "admin"}

if "customers" not in st.session_state:
    st.session_state.customers = pd.DataFrame({
        "Name": ["Rahul", "Anita", "Kiran"],
        "Age": [34, 29, 41],
        "Balance": [50000, 32000, 88000],
        "Loan": ["No", "Yes", "Yes"]
    })

# ---------------- AUTH FUNCTIONS ----------------
def login_user(email, password):
    return email in st.session_state.users and st.session_state.users[email] == password

def register_user(email, password):
    if email in st.session_state.users:
        return False
    st.session_state.users[email] = password
    return True

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🏦 AI Banking Platform")

    option = st.radio("Select Option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.logged_in = True
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        if st.button("Register"):
            if register_user(email, password):
                st.success("Registration successful. Please login.")
            else:
                st.error("User already exists")

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("🏦 AI Banking Intelligence Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", len(st.session_state.customers))
    c2.metric("Active Accounts", "39,842")
    c3.metric("High Risk", "12%")
    c4.metric("Retention Rate", "88%")

    st.subheader("📊 Customer Risk Distribution")
    risk_data = {"Low": 28, "Medium": 12, "High": 5}
    st.bar_chart(risk_data)

# ---------------- CUSTOMER MANAGEMENT ----------------
def customer_management():
    st.title("👥 Customer Management")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Add New Customer")
        name = st.text_input("Customer Name")
        age = st.number_input("Age", 18, 80)
        balance = st.number_input("Account Balance", value=10000)
        loan = st.selectbox("Loan Taken", ["Yes", "No"])

        if st.button("Add Customer"):
            new_customer = pd.DataFrame([[name, age, balance, loan]],
                                        columns=["Name", "Age", "Balance", "Loan"])
            st.session_state.customers = pd.concat(
                [st.session_state.customers, new_customer],
                ignore_index=True
            )
            st.success("Customer added successfully")

    with col2:
        st.subheader("📋 Existing Customers")
        st.dataframe(st.session_state.customers, use_container_width=True)

# ---------------- RISK PREDICTION ----------------
def risk_prediction():
    st.title("🔮 Risk Prediction")

    st.subheader("Enter Customer Details")

    age = st.slider("Age", 18, 80, 30)
    balance = st.number_input("Account Balance", 0, 200000, 25000)
    loan = st.selectbox("Loan Taken", ["Yes", "No"])

    if st.button("Predict Risk"):
        if balance < 20000 and loan == "Yes":
            st.error("⚠️ High Risk Customer")
        elif balance < 50000:
            st.warning("⚠️ Medium Risk Customer")
        else:
            st.success("✅ Low Risk Customer")

# ---------------- REPORTS ----------------
def reports():
    st.title("📈 Banking Reports")

    st.subheader("Customer Growth")

    growth = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Customers": [1000, 1500, 2200, 3000, 4200]
    })

    st.line_chart(growth.set_index("Month"))

    st.info("Customer base is growing steadily 📈")

# ---------------- MAIN APP ----------------
def main_app():
    with st.sidebar:
        st.markdown("### 🏦 AI Banking Platform")

        st.markdown(
            """
            <div style='background:#1f7a4d;padding:10px;border-radius:8px;
            color:white;text-align:center;margin-bottom:15px;'>
            ✅ Logged In
            </div>
            """,
            unsafe_allow_html=True
        )

        menu = st.radio(
            "Navigation",
            [
                "📊 Dashboard",
                "👥 Customer Management",
                "🔮 Risk Prediction",
                "📈 Reports",
            ],
        )

        st.markdown("<br><br><br>", unsafe_allow_html=True)

        if st.button("🚪 Sign Out"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 Dashboard":
        dashboard()
    elif menu == "👥 Customer Management":
        customer_management()
    elif menu == "🔮 Risk Prediction":
        risk_prediction()
    elif menu == "📈 Reports":
        reports()

# ---------------- RUN ----------------
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
