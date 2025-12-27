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
# SAFE DATA LOADER (CRITICAL FIX)
# -------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "data/bank_marketing.csv",
            sep=";",
            engine="python",
            encoding="utf-8"
        )
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    # Normalize columns
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # 🔒 HARD CHECK (prevents KeyError forever)
    required_cols = {"balance", "campaign", "y"}
    missing = required_cols - set(df.columns)

    if missing:
        st.error(f"Dataset is missing required columns: {missing}")
        st.write("Detected columns:", df.columns.tolist())
        st.stop()

    return df

data = load_data()

# -------------------------------------------------
# BACKGROUND IMAGE
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
        padding: 22px;
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
        <div style="width:420px;margin:120px auto;padding:35px;
        background:rgba(15,23,42,0.95);border-radius:16px;text-align:center;">
        <h2>Customer Analysis Platform</h2>
        <p>Customer Intelligence & Risk Prediction System</p>
        """,
        unsafe_allow_html=True
    )

    option = st.radio("Select Option", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register" and st.button("Register"):
        st.session_state.users[email] = password
        st.success("Registered successfully")

    if option == "Login" and st.button("Login"):
        if st.session_state.users.get(email) == password:
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
        ["Dashboard", "View Customers", "Customer Prediction"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # -------------------------------------------------
    # SAFE RISK CALCULATION (NO KEYERROR)
    # -------------------------------------------------
    data["risk"] = "Low Risk"
    data.loc[
        (data["balance"].astype(float) < 0) &
        (data["campaign"].astype(int) > 2),
        "risk"
    ] = "High Risk"

    total_customers = len(data)
    high_risk_pct = round((data["risk"] == "High Risk").mean() * 100, 2)
    retention_rate = round((data["y"] == "yes").mean() * 100, 2)

    # -------------------------------------------------
    # DASHBOARD VIEW
    # -------------------------------------------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total_customers}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention_rate}%</h2></div>", unsafe_allow_html=True)

        fig = px.pie(data, names="risk", hole=0.4, title="Customer Risk Distribution")
        st.plotly_chart(fig, use_container_width=True)

    if menu == "View Customers":
        st.dataframe(data.head(100), use_container_width=True)

    if menu == "Customer Prediction":
        balance = st.number_input("Account Balance")
        campaign = st.slider("Campaign Contacts", 1, 10)

        if st.button("Predict"):
            risk = "High Risk" if balance < 0 and campaign > 2 else "Low Risk"
            st.success(f"Predicted Risk: {risk}")

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
