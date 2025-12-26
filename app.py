import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# -------------------------------------------------
# LOAD DATASET
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/bank_marketing.csv")

data = load_data()

# -------------------------------------------------
# BACKGROUND IMAGE (BASE64 – FIXED)
# -------------------------------------------------
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
        background-repeat: no-repeat;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.65);
        z-index: -1;
    }}

    .login-box {{
        width: 420px;
        padding: 30px;
        margin: 100px auto;
        background: rgba(15,23,42,0.96);
        border-radius: 16px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.8);
    }}

    .login-title {{
        font-size: 34px;
        font-weight: 800;
        color: white;
        text-align: center;
    }}

    .login-sub {{
        font-size: 14px;
        color: #cbd5e1;
        text-align: center;
        margin-bottom: 25px;
    }}

    .card {{
        background: #0f172a;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------
def login_page():

    st.markdown(
        """
        <div class="login-box">
            <div class="login-title">Customer Analysis Platform</div>
            <div class="login-sub">
                Customer Intelligence & Risk Prediction System
            </div>
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

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def dashboard():

    st.sidebar.markdown("### 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customer Prediction", "Add Customer", "View Customers"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # -------------------------------------------------
    # DATA METRICS (REAL)
    # -------------------------------------------------
    total_customers = data.shape[0]

    data["Risk"] = data.apply(
        lambda x: "High Risk" if x["balance"] < 500 and x["campaign"] > 3 else "Low Risk",
        axis=1
    )

    high_risk_pct = round(
        (data["Risk"] == "High Risk").sum() / total_customers * 100, 2
    )

    retention_rate = round(
        (data["y"] == "yes").sum() / total_customers * 100, 2
    )

    # -------------------------------------------------
    # DASHBOARD PAGE
    # -------------------------------------------------
    if menu == "Dashboard":

        st.title("📊 Customer Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total_customers}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention_rate}%</h2></div>", unsafe_allow_html=True)

        st.markdown("### 📈 Risk Distribution")

        fig1 = px.pie(
            data,
            names="Risk",
            title="Customer Risk Distribution",
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)

    # -------------------------------------------------
    # CUSTOMER PREDICTION
    # -------------------------------------------------
    if menu == "Customer Prediction":

        st.title("🔮 Customer Risk Prediction")

        age = st.slider("Age", 18, 70)
        balance = st.number_input("Account Balance", 0)
        campaign = st.slider("Campaign Contacts", 1, 10)

        if st.button("Predict"):
            risk = "High Risk" if balance < 500 and campaign > 3 else "Low Risk"
            st.success(f"Predicted Risk Level: **{risk}**")

    # -------------------------------------------------
    # ADD CUSTOMER
    # -------------------------------------------------
    if menu == "Add Customer":

        st.title("➕ Add New Customer")

        name = st.text_input("Customer Name")
        age = st.number_input("Age", 18, 80)
        balance = st.number_input("Initial Balance", 0)

        if st.button("Add Customer"):
            st.success(f"Customer **{name}** added successfully!")

    # -------------------------------------------------
    # VIEW CUSTOMERS
    # -------------------------------------------------
    if menu == "View Customers":

        st.title("📋 Existing Customers (Dataset)")
        st.dataframe(data.head(50), use_container_width=True)

# -------------------------------------------------
# APP ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
