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
# SESSION STATE INIT (CRITICAL)
# -------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

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
        min-height: 300px;
        margin: 100px auto;
        padding: 28px;
        background: rgba(15,23,42,0.96);
        border-radius: 16px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.75);
    }}

    .login-title {{
        font-size: 32px;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 6px;
    }}

    .login-sub {{
        font-size: 14px;
        color: #cbd5e1;
        text-align: center;
        margin-bottom: 22px;
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
            <div class="login-title">🏦 Customer Analysis Platform</div>
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

    # Sidebar
    st.sidebar.markdown("### 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "Customer Prediction", "View Customers"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # -------------------------------------------------
    # DASHBOARD HOME
    # -------------------------------------------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        col1, col2, col3 = st.columns(3)
        col1.markdown("<div class='card'><h3>Total Customers</h3><h2>{}</h2></div>".format(len(st.session_state.customers)), unsafe_allow_html=True)
        col2.markdown("<div class='card'><h3>High Risk</h3><h2>12%</h2></div>", unsafe_allow_html=True)
        col3.markdown("<div class='card'><h3>Retention Rate</h3><h2>88%</h2></div>", unsafe_allow_html=True)

        if st.session_state.customers:
            df = pd.DataFrame(st.session_state.customers)
            fig = px.histogram(df, x="Age", title="Customer Age Distribution")
            st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # ADD CUSTOMER
    # -------------------------------------------------
    if menu == "Add Customer":
        st.title("➕ Add New Customer")

        name = st.text_input("Customer Name")
        age = st.number_input("Age", 18, 80)
        balance = st.number_input("Initial Balance", 0)

        if st.button("Add Customer"):
            customer = {
                "Name": name,
                "Age": age,
                "Balance": balance
            }
            st.session_state.customers.append(customer)
            st.success(f"Customer **{name}** added successfully!")

    # -------------------------------------------------
    # CUSTOMER PREDICTION
    # -------------------------------------------------
    if menu == "Customer Prediction":
        st.title("🔮 Customer Risk Prediction")

        age = st.slider("Age", 18, 70)
        balance = st.number_input("Account Balance", 0)
        transactions = st.slider("Monthly Transactions", 1, 100)

        if st.button("Predict Risk"):
            risk = "High Risk" if balance < 5000 and transactions < 10 else "Low Risk"
            st.success(f"Predicted Risk Level: **{risk}**")

    # -------------------------------------------------
    # VIEW CUSTOMERS
    # -------------------------------------------------
    if menu == "View Customers":
        st.title("👥 Existing Customers")

        if not st.session_state.customers:
            st.warning("No customers added yet.")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.pie(df, names="Name", values="Balance", title="Balance Distribution")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.histogram(df, x="Age", nbins=10, title="Age Frequency")
                st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# APP ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
