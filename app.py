import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3
import base64

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# DATABASE (LOGIN PERSISTENCE)
# =================================================
conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

# =================================================
# SESSION STATE
# =================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "customers" not in st.session_state:
    st.session_state.customers = []

# =================================================
# LOAD DATASET
# =================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_data = load_data()

# =================================================
# BACKGROUND IMAGE
# =================================================
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
# LOGIN / REGISTER
# =================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;border-radius:18px;color:white;text-align:center;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>ML-Driven Risk & Retention Analysis</p>
        """,
        unsafe_allow_html=True
    )

    mode = st.radio("Select", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if mode == "Register":
        if st.button("Register"):
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            if cur.fetchone():
                st.warning("User already exists. Please login.")
            else:
                cur.execute("INSERT INTO users VALUES (?,?)", (email, password))
                conn.commit()
                st.success("Registration successful")

    if mode == "Login":
        if st.button("Login"):
            cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            if cur.fetchone():
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# ML MODEL (LOGISTIC REGRESSION)
# =================================================
@st.cache_data
def train_model(df):
    data = df.copy()

    le = LabelEncoder()
    for col in ["job", "marital", "education", "housing", "loan"]:
        data[col] = le.fit_transform(data[col].astype(str))

    X = data[["age", "balance", "campaign"]]
    y = data["y"].map({"yes": 1, "no": 0})

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    return model

model = train_model(bank_data)

# =================================================
# DASHBOARD
# =================================================
def dashboard():

    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customers", "View Customers", "Prediction"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Records</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>Subscribed</h3><h2>{(bank_data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Avg Balance</h3><h2>{bank_data['balance'].mean():.0f}</h2></div>", unsafe_allow_html=True)

        st.plotly_chart(px.histogram(bank_data, x="balance", title="Balance Distribution"), use_container_width=True)
        st.plotly_chart(px.pie(bank_data, names="y", title="Subscription Rate"), use_container_width=True)

        st.subheader("📋 Sample Dataset (First 50 Rows)")
        st.dataframe(bank_data.head(50), use_container_width=True)

    # ---------------- ADD CUSTOMERS ----------------
    if menu == "Add Customers":
        st.title("➕ Add Customers")

        mode = st.radio("Mode", ["Single", "Upload CSV"])

        if mode == "Single":
            name = st.text_input("Name")
            age = st.number_input("Age", 18, 100)
            balance = st.number_input("Balance")
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                st.session_state.customers.append({
                    "name": name,
                    "age": age,
                    "balance": balance,
                    "campaign": campaign
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV (name, age, balance, campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                st.session_state.customers.extend(df.to_dict("records"))
                st.success(f"{len(df)} customers added")

    # ---------------- VIEW ----------------
    if menu == "View Customers":
        st.title("👥 Customers")
        if st.session_state.customers:
            st.dataframe(pd.DataFrame(st.session_state.customers), use_container_width=True)
        else:
            st.info("No customers added")

    # ---------------- PREDICTION ----------------
    if menu == "Prediction":
        st.title("🔮 ML Risk Prediction")

        if not st.session_state.customers:
            st.warning("Add customers first")
            return

        df = pd.DataFrame(st.session_state.customers)
        selected = st.selectbox("Select Customer", df["name"])
        c = df[df["name"] == selected].iloc[0]

        prob = model.predict_proba([[c["age"], c["balance"], c["campaign"]]])[0][1]

        st.metric("Subscription Probability", f"{prob*100:.2f}%")

        st.plotly_chart(
            px.scatter(df, x="campaign", y="balance", title="Campaign vs Balance"),
            use_container_width=True
        )

# =================================================
# ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
