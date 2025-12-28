import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import sqlite3

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
# DATABASE (USER AUTH)
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
# LOAD BANK DATASET
# =================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_data = load_bank_data()

# =================================================
# TRAIN LOGISTIC REGRESSION MODEL
# =================================================
@st.cache_data
def train_model(df):
    data = df.copy()

    le = LabelEncoder()
    for col in data.select_dtypes(include="object").columns:
        data[col] = le.fit_transform(data[col])

    X = data.drop("y", axis=1)
    y = data["y"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    return model

ml_model = train_model(bank_data)

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
# LOGIN PAGE (NO RE-REGISTER NEEDED)
# =================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;border-radius:18px;
        color:white;text-align:center;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>ML-Based Customer Risk & Retention</p>
        """,
        unsafe_allow_html=True
    )

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Login"):
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        if cur.fetchone():
            st.session_state.logged_in = True
            st.session_state.current_user = email
            st.rerun()
        else:
            st.error("Invalid credentials")

    if col2.button("Register"):
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            st.warning("User already registered. Please login.")
        else:
            cur.execute("INSERT INTO users VALUES (?,?)", (email, password))
            conn.commit()
            st.success("Registered successfully. Now login.")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RISK RULE (DISPLAY PURPOSE)
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

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        bank_data["risk"] = bank_data.apply(
            lambda x: calculate_risk(x["balance"], x["campaign"]),
            axis=1
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(bank_data['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(bank_data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(bank_data, names="risk"), use_container_width=True)
        col2.plotly_chart(px.histogram(bank_data, x="balance"), use_container_width=True)

        st.subheader("📋 Sample Dataset (First 50 Rows)")
        st.dataframe(bank_data.head(50), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        option = st.radio("Add Mode", ["Single Customer", "Multiple Customers (CSV)"])

        if option == "Single Customer":
            name = st.text_input("Customer Name")
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": calculate_risk(balance, campaign)
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV (name, balance, campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                df.columns = df.columns.str.lower()
                for _, r in df.iterrows():
                    st.session_state.customers.append({
                        "name": r["name"],
                        "balance": r["balance"],
                        "campaign": r["campaign"],
                        "risk": calculate_risk(r["balance"], r["campaign"])
                    })
                st.success(f"{len(df)} customers added")

    # ---------------- VIEW CUSTOMERS ----------------
    if menu == "View Customers":
        st.title("👥 Customers")

        if not st.session_state.customers:
            st.info("No customers added")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

    # ---------------- PREDICTION ----------------
    if menu == "Prediction":
        st.title("🔮 ML-Based Risk Prediction")

        if not st.session_state.customers:
            st.warning("Please add customers first")
            st.stop()

        df = pd.DataFrame(st.session_state.customers)
        selected = st.selectbox("Select Customer", df["name"])
        cust = df[df["name"] == selected].iloc[0]

        st.success(f"Predicted Risk Category: **{cust['risk']}**")

        st.plotly_chart(
            px.scatter(df, x="campaign", y="balance", color="risk", hover_data=["name"]),
            use_container_width=True
        )

# =================================================
# ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
