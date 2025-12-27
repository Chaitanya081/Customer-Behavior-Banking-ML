# ==========================================================
# CUSTOMER ANALYSIS PLATFORM – FULL INDUSTRY DEMO APPLICATION
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# SESSION STATE INITIALIZATION
# ==========================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

# ==========================================================
# LOAD BANK DATASET (REFERENCE DATA)
# ==========================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        quotechar='"',
        engine="python"
    )
    df.columns = df.columns.str.strip().str.lower()
    return df

bank_data = load_bank_data()

# ==========================================================
# BACKGROUND IMAGE (BASE64)
# ==========================================================
def load_bg(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = load_bg("images/loginimage.jpg")

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
        background: rgba(0,0,0,0.7);
        z-index: -1;
    }}
    .card {{
        background:#020617;
        padding:22px;
        border-radius:14px;
        color:white;
        text-align:center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# RISK CALCULATION LOGIC (EXPLAINABLE)
# ==========================================================
def calculate_risk(balance, campaign):
    if balance < 0 and campaign >= 3:
        return "High Risk"
    elif balance < 5000 and campaign >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"

# ==========================================================
# LOGIN / REGISTER PAGE
# ==========================================================
def login_page():
    st.markdown(
        """
        <div style="
            width:420px;
            margin:120px auto;
            background:#020617;
            padding:32px;
            border-radius:18px;
            color:white;
            text-align:center;
        ">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>Secure Login / Registration</p>
        """,
        unsafe_allow_html=True
    )

    option = st.radio("Select Option", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if email in st.session_state.users:
                st.error("User already exists")
            else:
                st.session_state.users[email] = password
                st.success("Registration successful")

    if option == "Login":
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# DASHBOARD / MAIN APP
# ==========================================================
def dashboard():

    # ---------------- SIDEBAR ----------------
    st.sidebar.markdown("### 👤 Logged User")
    st.sidebar.success(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ======================================================
    # DASHBOARD PAGE
    # ======================================================
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        data = bank_data.copy()
        data["risk"] = data.apply(
            lambda x: calculate_risk(x["balance"], x["campaign"]),
            axis=1
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Records</h3><h2>{len(data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(data['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(data, names="risk", title="Risk Distribution"), use_container_width=True)
        col2.plotly_chart(px.histogram(data, x="balance", title="Balance Distribution"), use_container_width=True)

        st.subheader("Dataset Preview")
        st.dataframe(data.head(30), use_container_width=True)

    # ======================================================
    # ADD CUSTOMER PAGE
    # ======================================================
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        count = st.number_input(
            "How many customers do you want to add?",
            min_value=1,
            step=1
        )

        # -------- SINGLE CUSTOMER --------
        if count == 1:
            name = st.text_input("Customer Name")
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": calculate_risk(balance, campaign),
                    "added_on": datetime.now()
                })
                st.success("Customer added successfully")

        # -------- MULTIPLE CUSTOMERS --------
        else:
            st.info("Upload CSV with columns: name, balance, campaign")
            file = st.file_uploader("Upload CSV", type=["csv"])

            if file:
                df = pd.read_csv(file)
                df.columns = df.columns.str.lower()

                for _, row in df.iterrows():
                    st.session_state.customers.append({
                        "name": row["name"],
                        "balance": row["balance"],
                        "campaign": row["campaign"],
                        "risk": calculate_risk(row["balance"], row["campaign"]),
                        "added_on": datetime.now()
                    })

                st.success("Multiple customers added successfully")

    # ======================================================
    # VIEW & DELETE CUSTOMERS (DELETE IS HERE – ALWAYS VISIBLE)
    # ======================================================
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        st.write("Total customers stored:", len(st.session_state.customers))

        if len(st.session_state.customers) == 0:
            st.warning("No customers available")
        else:
            df = pd.DataFrame(st.session_state.customers)

            st.subheader("Customer Records")
            st.dataframe(df, use_container_width=True)

            st.subheader("🗑 Delete Customers")

            selected = st.multiselect(
                "Select customer(s) to delete",
                options=df["name"].tolist()
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Delete Selected"):
                    st.session_state.customers = [
                        c for c in st.session_state.customers
                        if c["name"] not in selected
                    ]
                    st.success("Selected customers deleted")
                    st.rerun()

            with col2:
                if st.button("Delete ALL Customers"):
                    st.session_state.customers.clear()
                    st.warning("All customers deleted")
                    st.rerun()

    # ======================================================
    # PREDICTION PAGE (FULL CUSTOMER DATA SHOWN)
    # ======================================================
    if menu == "Prediction":
        st.title("🔮 Customer Risk Prediction")

        if len(st.session_state.customers) == 0:
            st.warning("Please add customers first")
        else:
            df = pd.DataFrame(st.session_state.customers)

            selected_name = st.selectbox(
                "Select Customer",
                df["name"].tolist()
            )

            cust = df[df["name"] == selected_name].iloc[0]

            st.subheader("Customer Details")
            st.json({
                "Name": cust["name"],
                "Balance": cust["balance"],
                "Campaign Calls": cust["campaign"],
                "Predicted Risk": cust["risk"],
                "Added On": str(cust["added_on"])
            })

# ==========================================================
# APPLICATION ROUTER
# ==========================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
