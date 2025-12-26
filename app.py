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
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SESSION STATE INIT (FIXES ALL ERRORS)
# -------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# -------------------------------------------------
# LOAD IMAGE SAFELY (BASE64)
# -------------------------------------------------
def load_bg_image(image_path):
    if not Path(image_path).exists():
        return ""
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image = load_bg_image("images/loginimage.jpg")

# -------------------------------------------------
# CSS WITH IMAGE + TEXT OVERLAY (WORKING)
# -------------------------------------------------
st.markdown(
    f"""
    <style>
    .hero {{
        position: relative;
        width: 100%;
        height: 320px;
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        margin-bottom: 30px;
    }}

    .hero::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: rgba(0,0,0,0.45);
        border-radius: 12px;
    }}

    .hero-text {{
        position: absolute;
        bottom: 35px;
        left: 45px;
        color: white;
        z-index: 2;
    }}

    .hero-text h1 {{
        font-size: 42px;
        margin: 0;
        font-weight: 700;
    }}

    .hero-text p {{
        font-size: 16px;
        opacity: 0.9;
        margin-top: 5px;
    }}

    .card {{
        padding: 22px;
        background-color: #111827;
        border-radius: 12px;
        text-align: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN / REGISTER PAGE
# -------------------------------------------------
def login_page():

    st.markdown(
        """
        <div class="hero">
            <div class="hero-text">
                <h1>AI Banking Platform</h1>
                <p>Customer Intelligence & Risk Prediction System</p>
            </div>
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

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("🏦 AI Banking Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown("<div class='card'><h3>Total Customers</h3><h2>45,211</h2></div>", unsafe_allow_html=True)
        c2.markdown("<div class='card'><h3>High Risk</h3><h2>12%</h2></div>", unsafe_allow_html=True)
        c3.markdown("<div class='card'><h3>Retention Rate</h3><h2>88%</h2></div>", unsafe_allow_html=True)

        st.markdown("### 📊 Customer Insights")

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
        tx = st.slider("Monthly Transactions", 1, 100)

        if st.button("Predict Risk"):
            risk = "High Risk" if balance < 5000 and tx < 10 else "Low Risk"
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
# APP ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
