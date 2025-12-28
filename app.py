import streamlit as st
import pandas as pd
import plotly.express as px
import base64

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

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
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

# =================================================
# LOAD BANK DATASET
# =================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        quotechar='"',
        engine="python"
    )
    df.columns = df.columns.str.lower().str.strip()
    return df

bank_data = load_bank_data()

# =================================================
# TRAIN ML MODEL (RUNS ONCE)
# =================================================
@st.cache_resource
def train_model(df):
    data = df.copy()

    le = LabelEncoder()
    data["y"] = le.fit_transform(data["y"])

    X = data[["balance", "campaign"]]
    y = data["y"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    return model

model = train_model(bank_data)

# =================================================
# BACKGROUND IMAGE
# =================================================
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
        background: rgba(0,0,0,0.70);
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
# LOGIN PAGE
# =================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;border-radius:18px;
        color:white;text-align:center;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>Customer Intelligence & Risk Prediction</p>
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
# DASHBOARD
# =================================================
def dashboard():

    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        # Risk via ML probabilities
        probs = model.predict_proba(bank_data[["balance", "campaign"]])[:, 1]

        bank_data["risk"] = pd.cut(
            probs,
            bins=[-1, 0.4, 0.7, 1.0],
            labels=["Low Risk", "Medium Risk", "High Risk"]
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(bank_data['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(bank_data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(bank_data, names="risk", title="Risk Distribution"), use_container_width=True)
        with col2:
            st.plotly_chart(px.histogram(bank_data, x="balance", title="Balance Distribution"), use_container_width=True)

        st.subheader("📋 Sample Dataset (First 100 Rows)")
        st.dataframe(bank_data.head(100), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        count = st.number_input("How many customers to add?", min_value=1, step=1)

        if count == 1:
            name = st.text_input("Customer Name")
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                prob = model.predict_proba([[balance, campaign]])[0][1]
                risk = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.4 else "Low Risk"

                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": risk
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV (name,balance,campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                for _, r in df.iterrows():
                    prob = model.predict_proba([[r["balance"], r["campaign"]]])[0][1]
                    risk = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.4 else "Low Risk"

                    st.session_state.customers.append({
                        "name": r["name"],
                        "balance": r["balance"],
                        "campaign": r["campaign"],
                        "risk": risk
                    })
                st.success("Multiple customers added")

    # ---------------- VIEW + DELETE ----------------
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.info("No customers added")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

            st.markdown("### 🗑 Delete Customers")
            selected = st.multiselect("Select customers", df["name"].tolist())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete Selected"):
                    st.session_state.customers = [
                        c for c in st.session_state.customers if c["name"] not in selected
                    ]
                    st.success("Deleted selected")
                    st.rerun()

            with col2:
                if st.button("Delete ALL"):
                    st.session_state.customers.clear()
                    st.warning("All deleted")
                    st.rerun()

    # ---------------- PREDICTION ----------------
    if menu == "Prediction":
        st.title("🔮 Risk Prediction")

        if not st.session_state.customers:
            st.warning("Add customers first")
            st.stop()

        df = pd.DataFrame(st.session_state.customers)
        selected = st.selectbox("Select Customer", df["name"])
        cust = df[df["name"] == selected].iloc[0]

        st.markdown(
            f"""
            <div style="background:#020617;padding:24px;border-radius:16px;color:white;">
            <h3>Customer Details</h3>
            <b>Name:</b> {cust['name']}<br>
            <b>Balance:</b> {cust['balance']}<br>
            <b>Campaign Calls:</b> {cust['campaign']}<br>
            <b>Predicted Risk:</b>
            <span style="font-size:22px;font-weight:800;">{cust['risk']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# =================================================
# APP ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
