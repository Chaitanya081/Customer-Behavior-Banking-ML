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
# SESSION STATE INIT
# -------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# -------------------------------------------------
# BACKGROUND IMAGE (BASE64 – ALWAYS LOADS)
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
        min-height: 320px;
        margin: 90px auto;
        padding: 30px;
        background: rgba(15,23,42,0.96);
        border-radius: 16px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.75);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    .login-title {{
        font-size: 34px;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 8px;
    }}

    .login-sub {{
        font-size: 14px;
        color: #cbd5e1;
        text-align: center;
        margin-bottom: 28px;
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
# LOGIN / REGISTER PAGE
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
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def dashboard():

    # ---------------- SIDEBAR ----------------
    st.sidebar.markdown("## 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧠 Live Customer Prediction")

    cust_name = st.sidebar.text_input("Customer Name")
    age = st.sidebar.slider("Age", 18, 70)
    balance = st.sidebar.number_input("Account Balance", 0)
    transactions = st.sidebar.slider("Monthly Transactions", 1, 100)

    risk_level = "Low Risk"
    if balance < 5000 and transactions < 10:
        risk_level = "High Risk"
    elif balance < 10000:
        risk_level = "Medium Risk"

    st.sidebar.info(f"**Predicted Risk:** {risk_level}")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ---------------- MAIN DASHBOARD ----------------
    st.title("📊 Customer Analysis Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.markdown("<div class='card'><h3>Total Customers</h3><h2>45,211</h2></div>", unsafe_allow_html=True)
    col2.markdown("<div class='card'><h3>High Risk</h3><h2>12%</h2></div>", unsafe_allow_html=True)
    col3.markdown("<div class='card'><h3>Retention Rate</h3><h2>88%</h2></div>", unsafe_allow_html=True)

    st.markdown("### 📈 Customer Risk Distribution")

    risk_df = pd.DataFrame({
        "Risk Level": ["Low Risk", "Medium Risk", "High Risk"],
        "Customers": [30000, 9000, 6211]
    })

    pie_fig = px.pie(
        risk_df,
        names="Risk Level",
        values="Customers",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(pie_fig, use_container_width=True)

    st.markdown("### 📊 Customer Segment Frequency")

    seg_df = pd.DataFrame({
        "Segment": ["Low Risk", "Medium Risk", "High Risk", "VIP"],
        "Count": [20000, 15000, 7000, 3000]
    })

    bar_fig = px.bar(
        seg_df,
        x="Segment",
        y="Count",
        color="Segment"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

# -------------------------------------------------
# APP ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
