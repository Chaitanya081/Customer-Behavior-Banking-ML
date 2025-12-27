import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide"
)

# =====================================================
# SESSION STATE INIT
# =====================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "customers" not in st.session_state:
    st.session_state.customers = []

# =====================================================
# BACKGROUND IMAGE
# =====================================================
def load_bg(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = load_bg("images/loginimage.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg}");
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
    .glass {{
        background: rgba(15,23,42,0.96);
        padding: 40px;
        border-radius: 18px;
        width: 450px;
        margin: auto;
        margin-top: 120px;
        box-shadow: 0 30px 80px rgba(0,0,0,0.8);
        text-align: center;
    }}
    .card {{
        background:#0f172a;
        padding:20px;
        border-radius:14px;
        text-align:center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOAD BANK DATASET (FOR DASHBOARD)
# =====================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        quotechar='"',
        engine="python"
    )
    df.columns = df.columns.str.strip().str.lower()
    return df

bank_data = load_bank_data()

# =====================================================
# RISK LOGIC
# =====================================================
def calculate_risk(balance, campaign):
    if balance < 0 and campaign >= 3:
        return "High Risk"
    elif campaign >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    st.markdown(
        """
        <div class="glass">
            <h2>🔐 Customer Analysis Platform</h2>
            <p style="color:#cbd5e1">Customer Intelligence & Risk System</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    option = st.radio("Select Option", ["Login", "Register"], horizontal=True)

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
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

# =====================================================
# DASHBOARD
# =====================================================
def dashboard():

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # ================= DASHBOARD =================
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        # Risk logic on dataset
        data = bank_data.copy()
        data["risk"] = "Low Risk"
        data.loc[(data["balance"] < 0) & (data["campaign"] > 2), "risk"] = "High Risk"

        total = len(data)
        high_risk_pct = round((data["risk"] == "High Risk").mean() * 100, 2)
        retention = round((data["y"] == "yes").mean() * 100, 2)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(data, names="risk", title="Risk Distribution")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(data, x="balance", title="Balance Distribution")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Dataset Preview")
        st.dataframe(data.head(20), use_container_width=True)

    # ================= ADD CUSTOMER =================
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        name = st.text_input("Customer Name")
        balance = st.number_input("Balance", value=0.0)
        campaign = st.number_input("Campaign Calls", value=0, step=1)

        if st.button("Add Customer"):
            st.session_state.customers.append({
                "name": name,
                "balance": balance,
                "campaign": campaign,
                "risk": calculate_risk(balance, campaign)
            })
            st.success("Customer added")

        st.markdown("---")
        st.subheader("📂 Upload Multiple Customers (CSV)")
        file = st.file_uploader("Upload CSV", type=["csv"])

        if file:
            df = pd.read_csv(file)
            for _, r in df.iterrows():
                st.session_state.customers.append({
                    "name": r["name"],
                    "balance": r["balance"],
                    "campaign": r["campaign"],
                    "risk": calculate_risk(r["balance"], r["campaign"])
                })
            st.success("CSV customers added")

    # ================= VIEW & DELETE =================
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.info("No customers added yet")
            return

        df = pd.DataFrame(st.session_state.customers)
        st.dataframe(df, use_container_width=True)

        selected = st.multiselect(
            "Select customers to delete",
            df["name"].tolist()
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete Selected"):
                st.session_state.customers = [
                    c for c in st.session_state.customers
                    if c["name"] not in selected
                ]
                st.experimental_rerun()

        with col2:
            if st.button("Delete ALL"):
                st.session_state.customers.clear()
                st.experimental_rerun()

    # ================= PREDICTION =================
    if menu == "Prediction":
        st.title("🔮 Risk Prediction")

        name = st.text_input("Customer Name")
        balance = st.number_input("Balance", value=0.0)
        campaign = st.number_input("Campaign Calls", value=0, step=1)

        if st.button("Predict"):
            risk = calculate_risk(balance, campaign)
            st.success(f"Customer **{name}** → **{risk}**")

            st.markdown("### Customer Details")
            st.json({
                "name": name,
                "balance": balance,
                "campaign": campaign,
                "predicted_risk": risk
            })

# =====================================================
# ROUTER
# =====================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
