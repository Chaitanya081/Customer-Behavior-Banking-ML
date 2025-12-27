import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide"
)

# =================================================
# SESSION STATE
# =================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "customers" not in st.session_state:
    st.session_state.customers = []

# =================================================
# BACKGROUND IMAGE
# =================================================
def bg_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = bg_image("images/loginimage.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg}");
        background-size: cover;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.65);
        z-index: -1;
    }}
    .card {{
        background:#0f172a;
        padding:20px;
        border-radius:14px;
        text-align:center;
        color:white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =================================================
# RISK LOGIC
# =================================================
def calculate_risk(balance, campaign):
    if balance < 0 and campaign >= 3:
        return "High Risk"
    elif campaign >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"

# =================================================
# LOGIN PAGE
# =================================================
def login_page():
    st.markdown("## 🔐 Customer Analysis Platform")

    option = st.radio("Select Option", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if email in st.session_state.users:
                st.error("User already exists")
            else:
                st.session_state.users[email] = password
                st.success("Registration successful. Please login.")

    if option == "Login":
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

# =================================================
# DASHBOARD
# =================================================
def dashboard():
    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        if not st.session_state.customers:
            st.info("No customers added yet.")
            return

        df = pd.DataFrame(st.session_state.customers)

        total = len(df)
        high_risk = round((df["risk"] == "High Risk").mean() * 100, 2)

        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk}%</h2></div>", unsafe_allow_html=True)

        fig = px.pie(df, names="risk", title="Risk Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    elif menu == "Add Customer":
        st.title("➕ Add Customer")

        name = st.text_input("Customer Name")
        balance = st.number_input("Balance", 0.0)
        campaign = st.number_input("Campaign Calls", 0, step=1)

        if st.button("Add Customer"):
            st.session_state.customers.append({
                "name": name,
                "balance": balance,
                "campaign": campaign,
                "risk": calculate_risk(balance, campaign)
            })
            st.success("Customer added")

        st.markdown("---")
        st.subheader("Upload CSV")

        file = st.file_uploader("CSV file", type=["csv"])
        if file:
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                st.session_state.customers.append({
                    "name": row["name"],
                    "balance": row["balance"],
                    "campaign": row["campaign"],
                    "risk": calculate_risk(row["balance"], row["campaign"])
                })
            st.success("CSV customers added")

    # ---------------- VIEW & DELETE ----------------
    elif menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.warning("No customers available")
            return

        df = pd.DataFrame(st.session_state.customers)
        st.dataframe(df, use_container_width=True)

        selected = st.multiselect(
            "Select customers to delete",
            df["name"].tolist()
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑 Delete Selected"):
                st.session_state.customers = [
                    c for c in st.session_state.customers
                    if c["name"] not in selected
                ]
                st.success("Selected customers deleted")
                st.rerun()

        with col2:
            if st.button("⚠ Delete ALL"):
                st.session_state.customers.clear()
                st.warning("All customers deleted")
                st.rerun()

    # ---------------- PREDICTION ----------------
    elif menu == "Prediction":
        st.title("🔮 Risk Prediction")

        name = st.text_input("Customer Name")
        balance = st.number_input("Balance", 0.0)
        campaign = st.number_input("Campaign Calls", 0)

        if st.button("Predict"):
            risk = calculate_risk(balance, campaign)

            st.markdown(
                f"""
                <div class='card'>
                <h3>Prediction Result</h3>
                <p><b>Name:</b> {name}</p>
                <p><b>Balance:</b> {balance}</p>
                <p><b>Campaign Calls:</b> {campaign}</p>
                <h2>{risk}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

# =================================================
# APP ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
