import streamlit as st
import pandas as pd
import plotly.express as px
import base64

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE
# =====================================================
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

# =====================================================
# LOAD BANK DATASET
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
# TRAIN ML MODEL (LOGISTIC REGRESSION)
# =====================================================
@st.cache_resource
def train_model(df):
    data = df.copy()

    data["y"] = LabelEncoder().fit_transform(data["y"])

    X = data[["balance", "campaign"]]
    y = data["y"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    return model

model = train_model(bank_data)

# =====================================================
# BACKGROUND IMAGE
# =====================================================
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

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;
        border-radius:18px;color:white;text-align:center;">
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

# =====================================================
# RISK LABEL FROM MODEL
# =====================================================
def risk_from_probability(prob):
    if prob > 0.7:
        return "High Risk"
    elif prob > 0.4:
        return "Medium Risk"
    else:
        return "Low Risk"

# =====================================================
# DASHBOARD
# =====================================================
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

    # ================= DASHBOARD =================
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        df = bank_data.copy()
        df["prob"] = model.predict_proba(df[["balance", "campaign"]])[:, 1]
        df["risk"] = df["prob"].apply(risk_from_probability)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(df['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(df['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df, names="risk", title="Risk Distribution"), use_container_width=True)
        with col2:
            st.plotly_chart(px.histogram(df, x="balance", title="Balance Distribution"), use_container_width=True)

        st.subheader("📋 Sample Dataset (First 50 Records)")
        st.dataframe(df.head(50), use_container_width=True)

    # ================= ADD CUSTOMER =================
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        mode = st.radio("Add Mode", ["Single Customer", "Multiple Customers (CSV)"])

        if mode == "Single Customer":
            name = st.text_input("Customer Name")
            age = st.number_input("Age", 18, 100, 25)
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                prob = model.predict_proba([[balance, campaign]])[0][1]
                st.session_state.customers.append({
                    "name": name,
                    "age": age,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": risk_from_probability(prob)
                })
                st.success("Customer added successfully")

        else:
            file = st.file_uploader("Upload CSV (name, age, balance, campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                df.columns = df.columns.str.lower()

                for _, r in df.iterrows():
                    prob = model.predict_proba([[r["balance"], r["campaign"]]])[0][1]
                    st.session_state.customers.append({
                        "name": r["name"],
                        "age": r["age"],
                        "balance": r["balance"],
                        "campaign": r["campaign"],
                        "risk": risk_from_probability(prob)
                    })
                st.success(f"{len(df)} customers added successfully")

    # ================= VIEW & DELETE =================
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.info("No customers added yet")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

            selected = st.multiselect("Select customers to delete", df["name"].tolist())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete Selected"):
                    st.session_state.customers = [
                        c for c in st.session_state.customers if c["name"] not in selected
                    ]
                    st.success("Selected customers deleted")
                    st.rerun()

            with col2:
                if st.button("Delete ALL"):
                    st.session_state.customers.clear()
                    st.warning("All customers deleted")
                    st.rerun()

    # ================= PREDICTION =================
    if menu == "Prediction":
        st.title("🔮 Risk Prediction")

        if not st.session_state.customers:
            st.warning("Please add customers first")
            return

        df = pd.DataFrame(st.session_state.customers)
        name = st.selectbox("Select Customer", df["name"])
        c = df[df["name"] == name].iloc[0]

        st.markdown(
            f"""
            <div style="background:#020617;padding:24px;border-radius:16px;color:white;">
            <h3>Customer Details</h3>
            <b>Name:</b> {c['name']}<br>
            <b>Age:</b> {c['age']}<br>
            <b>Balance:</b> {c['balance']}<br>
            <b>Campaign Calls:</b> {c['campaign']}<br>
            <b>Predicted Risk:</b>
            <span style="font-size:22px;font-weight:800;">{c['risk']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# =====================================================
# ROUTER
# =====================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
