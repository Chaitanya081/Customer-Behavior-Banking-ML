import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Banking Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
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
# LOAD IMAGE AS BASE64 (CRITICAL)
# -------------------------------------------------
def load_image(path):
    if not Path(path).exists():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = load_image("images/loginimage.jpg")

# -------------------------------------------------
# FULL PAGE BACKGROUND CSS
# -------------------------------------------------
st.markdown(
    f"""
    <style>
    /* MAIN APP BACKGROUND */
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* DARK OVERLAY */
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.65);
        z-index: -1;
    }}

    /* LOGIN CARD */
    .login-box {{
        max-width: 450px;
        margin-top: 80px;
        padding: 35px;
        background: rgba(15, 23, 42, 0.92);
        border-radius: 14px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }}

    .login-title {{
        font-size: 30px;
        font-weight: 700;
        color: white;
    }}

    .login-sub {{
        color: #cbd5e1;
        margin-bottom: 25px;
        font-size: 14px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------
def login_page():

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(
            """
            <div class="login-box">
                <div class="login-title">🏦 AI Banking Platform</div>
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

    st.sidebar.markdown("### 👤 User")
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

    if menu == "Dashboard":
        st.title("🏦 AI Banking Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Customers", "45,211")
        c2.metric("High Risk", "12%")
        c3.metric("Retention Rate", "88%")

        df = pd.DataFrame({
            "Segment": ["Low Risk", "Medium Risk", "High Risk", "VIP"],
            "Customers": [20000, 15000, 7000, 3000]
        })

        fig = px.bar(df, x="Segment", y="Customers", color="Segment")
        st.plotly_chart(fig, use_container_width=True)

    if menu == "Customer Prediction":
        st.title("🔮 Customer Risk Prediction")

        balance = st.number_input("Account Balance", 0)
        tx = st.slider("Monthly Transactions", 1, 100)

        if st.button("Predict"):
            risk = "High Risk" if balance < 5000 and tx < 10 else "Low Risk"
            st.success(f"Predicted Risk: {risk}")

    if menu == "Add Customer":
        st.title("➕ Add Customer")

        name = st.text_input("Customer Name")
        balance = st.number_input("Initial Balance", 0)

        if st.button("Add"):
            st.success(f"Customer {name} added!")

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
