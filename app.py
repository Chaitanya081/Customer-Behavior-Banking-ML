import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# SESSION STATE
# =================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

if "customers" not in st.session_state:
    st.session_state.customers = []

# =================================================
# LOAD BANK DATASET
# =================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower().str.strip()
    return df

bank_data = load_bank_data()

# =================================================
# BACKGROUND IMAGE
# =================================================
def get_bg(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = get_bg("images/loginimage.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg}");
        background-size: cover;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.7);
        z-index: -1;
    }}
    .card {{
        background:#020617;
        padding:22px;
        border-radius:14px;
        color:white;
        text-align:center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =================================================
# LOGIN
# =================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;
        border-radius:18px;color:white;text-align:center;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>Customer Intelligence & Risk Analytics</p>
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

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RISK LOGIC
# =================================================
def calculate_risk(balance, campaign):
    if balance < 0 or campaign >= 6:
        return "High Risk"
    elif balance < 5000 and campaign >= 3:
        return "Medium Risk"
    else:
        return "Low Risk"

# =================================================
# DASHBOARD
# =================================================
def dashboard():

    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        df = bank_data.copy()
        df["risk"] = df.apply(
            lambda x: calculate_risk(x["balance"], x["campaign"]),
            axis=1
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(df['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(df['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        st.plotly_chart(px.pie(df, names="risk"), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        mode = st.radio(
            "Add Mode",
            ["Single Customer", "Multiple Customers (CSV)"],
            horizontal=True
        )

        # SINGLE
        if mode == "Single Customer":
            with st.form("single_form", clear_on_submit=True):
                name = st.text_input("Customer Name")
                age = st.number_input("Age", 18, 100)
                balance = st.number_input("Balance", value=0.0)
                campaign = st.slider("Campaign Calls", 1, 10)

                submit = st.form_submit_button("Add Customer")

                if submit:
                    st.session_state.customers.append({
                        "id": len(st.session_state.customers) + 1,
                        "name": name,
                        "age": age,
                        "balance": balance,
                        "campaign": campaign,
                        "risk": calculate_risk(balance, campaign)
                    })
                    st.success(f"Customer '{name}' added")

        # MULTIPLE (SAFE)
        if mode == "Multiple Customers (CSV)":
            file = st.file_uploader(
                "Upload CSV (required: name, balance, campaign | optional: age)",
                type=["csv"]
            )

            if file:
                df = pd.read_csv(file)
                df.columns = df.columns.str.lower()

                if st.button("Add All Customers"):
                    for _, r in df.iterrows():
                        st.session_state.customers.append({
                            "id": len(st.session_state.customers) + 1,
                            "name": r.get("name", "Unknown"),
                            "age": r.get("age", None),
                            "balance": r.get("balance", 0),
                            "campaign": r.get("campaign", 1),
                            "risk": calculate_risk(
                                r.get("balance", 0),
                                r.get("campaign", 1)
                            )
                        })
                    st.success(f"{len(df)} customers added safely")

        if st.session_state.customers:
            st.subheader("📋 Customers Added")
            st.dataframe(pd.DataFrame(st.session_state.customers), use_container_width=True)

    # ---------------- VIEW & DELETE ----------------
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.info("No customers added")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

            selected = st.multiselect("Select customers to delete", df["name"].tolist())

            if st.button("Delete Selected"):
                st.session_state.customers = [
                    c for c in st.session_state.customers if c["name"] not in selected
                ]
                st.success("Selected customers deleted")
                st.rerun()

    # ---------------- PREDICTION ----------------
    if menu == "Prediction":
        st.title("🔮 Risk Prediction")

        if not st.session_state.customers:
            st.warning("Please add customers first")
            return

        df = pd.DataFrame(st.session_state.customers)
        name = st.selectbox("Select Customer", df["name"])
        cust = df[df["name"] == name].iloc[0]

        st.write(cust)

# =================================================
# ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
