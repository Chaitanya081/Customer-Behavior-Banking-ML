import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# SESSION STATE (IMPORTANT – NO ERRORS)
# -------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# -------------------------------------------------
# GLOBAL CSS (FULL PAGE IMAGE + CENTER BOX)
# -------------------------------------------------
st.markdown(
    """
    <style>

    /* Full page background */
    .stApp {
        background-image: url("images/loginimage.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Center container */
    .center-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 90vh;
    }

    /* Login Card (SMALLER SIZE – TEXT UNCHANGED) */
    .login-card {
        width: 420px;              /* ↓ reduced size */
        padding: 22px 26px;        /* ↓ reduced padding */
        background: rgba(8, 18, 36, 0.88);
        border-radius: 16px;
        box-shadow: 0 20px 45px rgba(0,0,0,0.55);
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .login-card h1 {
        font-size: 26px;
        margin-bottom: 6px;
        color: #ffffff;
    }

    .login-card p {
        font-size: 14px;
        color: #cfd8e3;
        margin-bottom: 18px;
    }

    /* Inputs */
    input {
        background-color: #111827 !important;
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN / REGISTER PAGE
# -------------------------------------------------
def login_page():

    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-card">
            <h1>🏦 AI Banking Platform</h1>
            <p>Customer Intelligence & Risk Prediction System</p>
        </div>
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
                st.success("Registration successful. Please login.")

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

    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customer Prediction", "Add Customer"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("🏦 AI Banking Intelligence Dashboard")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", "45,211")
        col2.metric("High Risk", "12%")
        col3.metric("Retention Rate", "88%")

        df = pd.DataFrame({
            "Segment": ["Low Risk", "Medium Risk", "High Risk", "VIP"],
            "Customers": [20000, 15000, 7000, 3000]
        })

        fig = px.bar(df, x="Segment", y="Customers", color="Segment")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- PREDICTION ----------------
    if menu == "Customer Prediction":
        st.title("🔮 Customer Risk Prediction")

        age = st.slider("Age", 18, 70)
        balance = st.number_input("Account Balance", 0)
        transactions = st.slider("Monthly Transactions", 1, 100)

        if st.button("Predict Risk"):
            risk = "High Risk" if balance < 5000 and transactions < 10 else "Low Risk"
            st.success(f"Predicted Risk Level: **{risk}**")

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add New Customer")

        name = st.text_input("Customer Name")
        age = st.number_input("Age", 18, 80)
        balance = st.number_input("Initial Balance", 0)

        if st.button("Add Customer"):
            st.success(f"Customer **{name}** added successfully!")

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()

