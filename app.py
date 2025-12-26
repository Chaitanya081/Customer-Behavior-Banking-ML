import streamlit as st
from auth import register_user, login_user

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="AI Banking Platform", layout="wide")

# -------------------- SESSION INIT --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------- BACKGROUND IMAGE + CSS --------------------
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(
                rgba(0,0,0,0.55),
                rgba(0,0,0,0.55)
            ),
            url("images/loginimage.jpg");
            background-size: cover;
            background-position: center;
        }

        .login-box {
            background: rgba(0, 0, 0, 0.65);
            padding: 30px;
            border-radius: 12px;
            width: 450px;
            margin-top: 40px;
        }

        label, h1, h3 {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# -------------------- LOGIN PAGE --------------------
def login_page():
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("## 🏦 AI Banking Platform")
        option = st.radio("Select Option", ["Login", "Register"])

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if option == "Register":
            if st.button("Register"):
                if register_user(email, password):
                    st.success("Registration successful. Please login.")
                else:
                    st.error("User already exists.")

        else:
            if st.button("Login"):
                if login_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.user = email
                    st.rerun()
                else:
                    st.error("Invalid email or password")

# -------------------- DASHBOARD --------------------
def dashboard():
    st.sidebar.markdown(f"### 👤 {st.session_state.user}")
    st.sidebar.success("Logged in")

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "Prediction", "Analytics"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    st.markdown("# 🏛 AI Banking Intelligence Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", "45,211")
    col2.metric("High Risk", "12%")
    col3.metric("Retention Rate", "88%")

    if menu == "Dashboard":
        st.info("Welcome! Advanced banking insights loaded.")

    if menu == "Add Customer":
        st.subheader("➕ Add New Customer")
        name = st.text_input("Customer Name")
        age = st.number_input("Age", 18, 100)
        income = st.number_input("Annual Income")
        if st.button("Save Customer"):
            st.success(f"Customer {name} added successfully!")

    if menu == "Prediction":
        st.subheader("📊 Risk Prediction")
        st.slider("Credit Score", 300, 900)
        st.button("Predict Risk")

    if menu == "Analytics":
        st.subheader("📈 Analytics Overview")
        st.success("Advanced analytics module ready")

# -------------------- ROUTER --------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
