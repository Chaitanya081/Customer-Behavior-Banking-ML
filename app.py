# =========================================================
# CUSTOMER ANALYSIS PLATFORM – INDUSTRY READY DEMO APP
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

# ---------------------------------------------------------
# LOAD DATASET (BANK MARKETING)
# ---------------------------------------------------------
@st.cache_data
def load_dataset():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        quotechar='"',
        engine="python"
    )
    df.columns = df.columns.str.strip().str.lower()
    return df

bank_data = load_dataset()

# ---------------------------------------------------------
# BACKGROUND IMAGE
# ---------------------------------------------------------
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64_image("images/loginimage.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_img}");
        background-size: cover;
        background-position: center;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.65);
        z-index: -1;
    }}
    .card {{
        background: #0f172a;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# RISK LOGIC (EXPLAINABLE – LOGISTIC STYLE RULE)
# ---------------------------------------------------------
def calculate_risk(balance, campaign):
    if balance < 0 and campaign > 2:
        return "High Risk"
    elif balance < 500 and campaign > 3:
        return "Medium Risk"
    else:
        return "Low Risk"

# ---------------------------------------------------------
# LOGIN / REGISTER
# ---------------------------------------------------------
def login_page():
    st.markdown(
        """
        <div class="card" style="max-width:420px;margin:auto;margin-top:120px;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>Login / Register</p>
        """,
        unsafe_allow_html=True
    )

    option = st.radio("Select", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if email in st.session_state.users:
                st.error("User already exists")
            else:
                st.session_state.users[email] = password
                st.success("Registered successfully")

    if option == "Login":
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
def dashboard():

    st.sidebar.markdown("### 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.experimental_rerun()

    # -----------------------------------------------------
    # DASHBOARD HOME
    # -----------------------------------------------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        data = bank_data.copy()
        data["risk"] = data.apply(
            lambda x: calculate_risk(x["balance"], x["campaign"]),
            axis=1
        )

        total_customers = len(data)
        high_risk_pct = round((data["risk"] == "High Risk").mean() * 100, 2)
        retention_rate = round((data["y"] == "yes").mean() * 100, 2)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total_customers}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention_rate}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(data, names="risk", title="Risk Distribution")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.histogram(data, x="balance", title="Balance Distribution")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Dataset Preview")
        st.dataframe(data.head(50), use_container_width=True)

    # -----------------------------------------------------
    # ADD CUSTOMER (SINGLE + MULTIPLE)
    # -----------------------------------------------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        option = st.radio("Mode", ["Single Customer", "Upload CSV"])

        if option == "Single Customer":
            name = st.text_input("Customer Name")
            balance = st.number_input("Balance")
            campaign = st.number_input("Campaign Calls", min_value=1)

            if st.button("Add Customer"):
                risk = calculate_risk(balance, campaign)
                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": risk,
                    "added_on": datetime.now()
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV", type=["csv"])
            if file:
                df = pd.read_csv(file)
                for _, row in df.iterrows():
                    st.session_state.customers.append({
                        "name": row.get("name", "Unknown"),
                        "balance": row["balance"],
                        "campaign": row["campaign"],
                        "risk": calculate_risk(row["balance"], row["campaign"]),
                        "added_on": datetime.now()
                    })
                st.success("Customers uploaded")

    # -----------------------------------------------------
    # VIEW + DELETE CUSTOMERS
    # -----------------------------------------------------
    if menu == "View Customers":
        st.title("👥 Customer Records")

        if not st.session_state.customers:
            st.info("No customers added")
            return

        df = pd.DataFrame(st.session_state.customers)
        st.dataframe(df, use_container_width=True)

        selected = st.multiselect("Select customers to delete", df["name"].tolist())

        if st.button("Delete Selected"):
            st.session_state.customers = [
                c for c in st.session_state.customers if c["name"] not in selected
            ]
            st.success("Deleted successfully")
            st.experimental_rerun()

        if st.button("Delete ALL"):
            st.session_state.customers.clear()
            st.warning("All customers deleted")
            st.experimental_rerun()

    # -----------------------------------------------------
    # PREDICTION PAGE
    # -----------------------------------------------------
    if menu == "Prediction":
        st.title("🔮 Customer Risk Prediction")

        name = st.text_input("Customer Name")
        balance = st.number_input("Balance", value=0.0)
        campaign = st.slider("Campaign Calls", 1, 10)

        if st.button("Predict"):
            risk = calculate_risk(balance, campaign)
            st.success(f"Customer **{name}** → **{risk}**")

            st.subheader("Customer Details")
            st.json({
                "Name": name,
                "Balance": balance,
                "Campaign Calls": campaign,
                "Predicted Risk": risk
            })

# ---------------------------------------------------------
# APP ROUTER
# ---------------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
