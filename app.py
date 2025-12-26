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
# LOAD DATASET
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/bank_marketing.csv")

data = load_data()

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
    .card {{
        background: #0f172a;
        padding: 25px;
        border-radius: 14px;
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
            <h2 style="text-align:center;color:white;">
            🏦 Customer Analysis Platform
            </h2>
            <p style="text-align:center;color:#cbd5e1;">
            Customer Intelligence & Risk Prediction System
            </p>
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

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def dashboard():

    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customer Prediction", "View Customers"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- METRICS ----------------
    total_customers = len(data)

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

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":

        st.title("📊 Customer Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total_customers}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention_rate}%</h2></div>", unsafe_allow_html=True)

        st.markdown("### 📈 Risk Distribution")
        fig1 = px.pie(data, names="Risk")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### 📉 Retention Analysis")
        fig2 = px.histogram(data, x="age", color="y")
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- PREDICTION ----------------
    if menu == "Customer Prediction":
        st.title("🔮 Customer Risk Prediction")

        age = st.slider("Age", 18, 90)
        balance = st.number_input("Balance")
        campaign = st.slider("Campaign Contacts", 1, 10)

        if st.button("Predict"):
            risk = "High Risk" if balance < 500 and campaign > 3 else "Low Risk"
            st.success(f"Predicted Risk: {risk}")

    # ---------------- VIEW CUSTOMERS ----------------
    if menu == "View Customers":
        st.title("👥 Customer Dataset")
        st.dataframe(data.head(100))

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
