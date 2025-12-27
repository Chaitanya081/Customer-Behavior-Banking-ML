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
# SESSION STATE
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
def bg_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = bg_image("images/loginimage.jpg")

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
        background: rgba(15,23,42,0.85);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
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
# LOAD MAIN DATASET (DASHBOARD ONLY)
# =====================================================
@st.cache_data
def load_dataset():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_df = load_dataset()

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
# LOGIN / REGISTER PAGE
# =====================================================
def login_page():
    st.markdown("<h1 style='text-align:center'>Customer Analysis Platform</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        option = st.radio("Choose Option", ["Login", "Register"])
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

        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# DASHBOARD (REAL DATASET)
# =====================================================
def dashboard_page():
    st.title("📊 Customer Intelligence Dashboard")

    df = bank_df.copy()
    df["risk"] = df.apply(lambda x: calculate_risk(x["balance"], x["campaign"]), axis=1)

    total = len(df)
    high_risk = round((df["risk"] == "High Risk").mean() * 100, 2)
    retention = round((df["y"] == "yes").mean() * 100, 2)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk}%</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention}%</h2></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, names="risk", title="Customer Risk Distribution",
                      color="risk",
                      color_discrete_map={
                          "High Risk":"#ef4444",
                          "Medium Risk":"#facc15",
                          "Low Risk":"#22c55e"
                      })
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.histogram(df, x="balance", nbins=40, title="Balance Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Customer Dataset Preview")
    st.dataframe(df.head(30), use_container_width=True)

# =====================================================
# ADD CUSTOMER
# =====================================================
def add_customer_page():
    st.title("➕ Add Customer")

    name = st.text_input("Customer Name")
    balance = st.number_input("Balance", step=100.0)
    campaign = st.number_input("Campaign Calls", step=1)

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

    file = st.file_uploader("Upload CSV (name,balance,campaign)", type=["csv"])
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

# =====================================================
# VIEW & DELETE
# =====================================================
def view_customers_page():
    st.title("👥 View & Delete Customers")

    if not st.session_state.customers:
        st.info("No customers added yet")
        return

    df = pd.DataFrame(st.session_state.customers)
    st.dataframe(df, use_container_width=True)

    selected = st.multiselect("Select customers to delete", df["name"].tolist())

    if st.button("🗑 Delete Selected"):
        st.session_state.customers = [c for c in st.session_state.customers if c["name"] not in selected]
        st.experimental_rerun()

    if st.button("⚠ Delete ALL"):
        st.session_state.customers.clear()
        st.experimental_rerun()

# =====================================================
# PREDICTION
# =====================================================
def prediction_page():
    st.title("🔮 Risk Prediction")

    name = st.text_input("Customer Name")
    balance = st.number_input("Balance", step=100.0)
    campaign = st.number_input("Campaign Calls", step=1)

    if st.button("Predict Risk"):
        risk = calculate_risk(balance, campaign)

        st.markdown(
            f"""
            <div class="glass">
            <h3>Prediction Result</h3>
            <p><b>Name:</b> {name}</p>
            <p><b>Balance:</b> {balance}</p>
            <p><b>Campaign Calls:</b> {campaign}</p>
            <p><b>Predicted Risk:</b> <span style="color:#22c55e">{risk}</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

# =====================================================
# MAIN ROUTER
# =====================================================
if st.session_state.logged_in:
    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    if menu == "Dashboard":
        dashboard_page()
    elif menu == "Add Customer":
        add_customer_page()
    elif menu == "View Customers":
        view_customers_page()
    elif menu == "Prediction":
        prediction_page()
else:
    login_page()
