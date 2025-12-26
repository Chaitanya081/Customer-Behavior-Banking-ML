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
# BACKGROUND IMAGE (BASE64)
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

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def dashboard():

    # SIDEBAR
    st.sidebar.markdown("### 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customer Prediction", "Add Customer", "Live Analysis"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Analysis Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown("<div class='card'><h3>Total Customers</h3><h2>45,211</h2></div>", unsafe_allow_html=True)
        c2.markdown("<div class='card'><h3>High Risk</h3><h2>12%</h2></div>", unsafe_allow_html=True)
        c3.markdown("<div class='card'><h3>Retention Rate</h3><h2>88%</h2></div>", unsafe_allow_html=True)

    # ---------------- CUSTOMER PREDICTION ----------------
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

    # ---------------- LIVE ANALYSIS (NEW) ----------------
    if menu == "Live Analysis":
        st.title("📈 Live Customer Risk Analysis")

        col1, col2 = st.columns(2)

        with col1:
            age = st.slider("Customer Age", 18, 70)
            balance = st.number_input("Account Balance", 0)
            transactions = st.slider("Monthly Transactions", 1, 100)

        risk = "Low Risk"
        if balance < 5000 and transactions < 10:
            risk = "High Risk"
        elif balance < 10000:
            risk = "Medium Risk"

        with col2:
            st.metric("Predicted Risk Level", risk)

        # PIE CHART
        risk_df = pd.DataFrame({
            "Risk": ["Low", "Medium", "High"],
            "Count": [30000, 9000, 6211]
        })

        pie = px.pie(
            risk_df,
            names="Risk",
            values="Count",
            hole=0.4,
            title="Customer Risk Distribution"
        )
        st.plotly_chart(pie, use_container_width=True)

        # BAR CHART
        freq_df = pd.DataFrame({
            "Transaction Range": ["Low", "Medium", "High"],
            "Customers": [15000, 20000, 10211]
        })

        bar = px.bar(
            freq_df,
            x="Transaction Range",
            y="Customers",
            title="Transaction Frequency Analysis",
            color="Transaction Range"
        )
        st.plotly_chart(bar, use_container_width=True)

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
