import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# SESSION STATE
# =================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

# =================================================
# LOAD BANK DATASET (FOR DASHBOARD)
# =================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_data = load_bank_data()

# =================================================
# BACKGROUND IMAGE
# =================================================
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

# =================================================
# LOGIN / REGISTER
# =================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;border-radius:18px;
        color:white;text-align:center;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>Customer Intelligence & Risk Prediction</p>
        """,
        unsafe_allow_html=True
    )

    option = st.radio("Select Option", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            st.session_state.users[email] = password
            st.success("Registered successfully")

    if option == "Login":
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RISK LOGIC
# =================================================
def calculate_risk(balance, campaign):
    if balance < 0 or campaign >= 6:
        return "High Risk"
    elif balance < 5000 and campaign >= 3:
        return "Medium Risk"
    else:
        return "Low Risk"

# =================================================
# DASHBOARD
# =================================================
def dashboard():

    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        bank_data["risk"] = bank_data.apply(
            lambda x: calculate_risk(x["balance"], x["campaign"]),
            axis=1
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(bank_data['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(bank_data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(bank_data, names="risk", title="Risk Distribution"), use_container_width=True)
        col2.plotly_chart(px.histogram(bank_data, x="balance", title="Balance Distribution"), use_container_width=True)

        st.subheader("📋 Sample Dataset Preview (First 50 Rows)")
        st.dataframe(bank_data.head(50), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        option = st.radio("Add Mode", ["Single Customer", "Multiple Customers (CSV)"])

        if option == "Single Customer":
            name = st.text_input("Customer Name")
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": calculate_risk(balance, campaign)
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV (name, balance, campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                df.columns = df.columns.str.lower()

                for _, r in df.iterrows():
                    st.session_state.customers.append({
                        "name": r["name"],
                        "balance": r["balance"],
                        "campaign": r["campaign"],
                        "risk": calculate_risk(r["balance"], r["campaign"])
                    })

                st.success(f"{len(df)} customers added")

    # ---------------- VIEW + DELETE ----------------
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.info("No customers added")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

            selected = st.multiselect("Select customers to delete", df["name"].tolist())

            col1, col2 = st.columns(2)
            if col1.button("Delete Selected"):
                st.session_state.customers = [
                    c for c in st.session_state.customers if c["name"] not in selected
                ]
                st.success("Selected customers deleted")
                st.rerun()

            if col2.button("Delete ALL"):
                st.session_state.customers.clear()
                st.warning("All customers deleted")
                st.rerun()

    # ---------------- PREDICTION ----------------
    if menu == "Prediction":
        st.title("🔮 Risk Prediction")

        if not st.session_state.customers:
            st.warning("Please add customers first")
            st.stop()

        df = pd.DataFrame(st.session_state.customers)
        selected = st.selectbox("Select Customer", df["name"])
        cust = df[df["name"] == selected].iloc[0]

        st.markdown(
            f"""
            <div style="background:#020617;padding:24px;border-radius:16px;color:white;">
            <b>Name:</b> {cust['name']}<br>
            <b>Balance:</b> {cust['balance']}<br>
            <b>Campaign Calls:</b> {cust['campaign']}<br>
            <b>Predicted Risk:</b>
            <span style="font-size:22px;font-weight:800;">{cust['risk']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📊 Prediction Insights")

        col1, col2 = st.columns(2)

        col1.plotly_chart(px.pie(df, names="risk", title="Risk Distribution"), use_container_width=True)

        avg_balance = df["balance"].mean()
        comp_df = pd.DataFrame({
            "Type": ["Selected", "Average"],
            "Balance": [cust["balance"], avg_balance]
        })
        col2.plotly_chart(px.bar(comp_df, x="Type", y="Balance", title="Balance Comparison"), use_container_width=True)

        st.plotly_chart(
            px.scatter(df, x="campaign", y="balance", color="risk", hover_data=["name"],
                       title="Campaign vs Balance"),
            use_container_width=True
        )

# =================================================
# APP ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
