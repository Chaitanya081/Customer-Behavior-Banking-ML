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
# SESSION STATE INIT (NO AUTO LOGIN)
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
# LOAD DATASET (YOUR FORMAT)
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        quotechar='"',
        engine="python"
    )
    df.columns = df.columns.str.strip().str.lower()
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
# LOGIN / REGISTER PAGE
# -------------------------------------------------
def login_page():
    st.markdown(
        """
        <div class="card" style="max-width:420px;margin:120px auto;">
            <h2>📊 Customer Analysis Platform</h2>
            <p style="color:#cbd5e1;">Customer Intelligence & Risk Prediction</p>
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
        ["Dashboard", "Add Customer", "View Customers", "Predict Customer"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # ---------------- RISK LOGIC ----------------
    df = data.copy()
    df["risk"] = "Low Risk"
    df.loc[
        (df["balance"] < 0) & (df["campaign"] > 2),
        "risk"
    ] = "High Risk"

    total_customers = len(df)
    high_risk_pct = round((df["risk"] == "High Risk").mean() * 100, 2)
    retention_rate = round((df["y"] == "yes").mean() * 100, 2)

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total_customers}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention_rate}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df, names="risk", title="Risk Distribution"), use_container_width=True)
        with col2:
            st.plotly_chart(px.histogram(df, x="balance", title="Balance Distribution"), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")
        name = st.text_input("Name")
        age = st.number_input("Age", 18, 100)
        balance = st.number_input("Balance")
        campaign = st.slider("Campaign Contacts", 1, 10)

        if st.button("Add"):
            risk = "High Risk" if balance < 0 and campaign > 2 else "Low Risk"
            st.session_state.customers.append(
                {"name": name, "age": age, "balance": balance, "campaign": campaign, "risk": risk}
            )
            st.success("Customer added")

    # ---------------- VIEW CUSTOMERS ----------------
    if menu == "View Customers":
        st.title("📋 Customers")
        if st.session_state.customers:
            st.dataframe(pd.DataFrame(st.session_state.customers), use_container_width=True)
        else:
            st.info("No customers added yet")

    # ---------------- PREDICT ----------------
    if menu == "Predict Customer":
        st.title("🔮 Predict Risk")
        balance = st.number_input("Balance")
        campaign = st.slider("Campaign", 1, 10)
        if st.button("Predict"):
            risk = "High Risk" if balance < 0 and campaign > 2 else "Low Risk"
            st.success(f"Predicted Risk: {risk}")

# -------------------------------------------------
# ROUTER (THIS IS THE KEY PART)
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
