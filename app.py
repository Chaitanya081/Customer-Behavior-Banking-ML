import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from sklearn.linear_model import LogisticRegression
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

if "model" not in st.session_state:
    st.session_state.model = None

# =================================================
# LOAD DATASET
# =================================================
@st.cache_data
def load_bank_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_data = load_bank_data()

# =================================================
# TRAIN LOGISTIC REGRESSION
# =================================================
def train_model(df):
    X = df[["balance", "campaign"]]
    y = (df["y"] == "yes").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model

if st.session_state.model is None:
    st.session_state.model = train_model(bank_data)

# =================================================
# BACKGROUND IMAGE
# =================================================
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = get_base64_image("images/loginimage.jpg")

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
            if email in st.session_state.users:
                st.warning("User already exists")
            else:
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
# RISK PREDICTION USING ML
# =================================================
def predict_risk(balance, campaign):
    prob = st.session_state.model.predict_proba([[balance, campaign]])[0][1]

    if prob > 0.6:
        return "High Risk"
    elif prob > 0.3:
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

        bank_data["risk"] = bank_data.apply(
            lambda x: predict_risk(x["balance"], x["campaign"]),
            axis=1
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(bank_data['risk']=='High Risk').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(bank_data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(bank_data, names="risk", title="Risk Distribution"), use_container_width=True)
        col2.plotly_chart(px.histogram(bank_data, x="balance", title="Balance Distribution"), use_container_width=True)

        st.subheader("📋 Sample Dataset (50 rows)")
        st.dataframe(bank_data.head(50), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        mode = st.radio("Add Mode", ["Single Customer", "Multiple Customers (CSV)"])

        if mode == "Single Customer":
            name = st.text_input("Customer Name")
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add Customer"):
                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": predict_risk(balance, campaign)
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV (name,balance,campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                for _, r in df.iterrows():
                    st.session_state.customers.append({
                        "name": r["name"],
                        "balance": r["balance"],
                        "campaign": r["campaign"],
                        "risk": predict_risk(r["balance"], r["campaign"])
                    })
                st.success(f"{len(df)} customers added")

    # ---------------- VIEW & DELETE ----------------
    if menu == "View Customers":
        st.title("👥 Customers")

        if not st.session_state.customers:
            st.info("No customers added")
        else:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)

            selected = st.multiselect("Select customers to delete", df["name"].tolist())

            col1, col2 = st.columns(2)
            if col1.button("Delete Selected"):
                st.session_state.customers = [
                    c for c in st.session_state.customers if c["name"] not in selected
                ]
                st.success("Deleted selected customers")
                st.rerun()

            if col2.button("Delete ALL"):
                st.session_state.customers.clear()
                st.warning("All customers deleted")
                st.rerun()

    # ---------------- PREDICTION ----------------
    if menu == "Prediction":
        st.title("🔮 ML-Based Risk Prediction")

        if not st.session_state.customers:
            st.warning("Add customers first")
            return

        df = pd.DataFrame(st.session_state.customers)
        selected = st.selectbox("Select Customer", df["name"])
        cust = df[df["name"] == selected].iloc[0]

        st.markdown(
            f"""
            <div style="background:#020617;padding:20px;border-radius:16px;color:white;">
            <b>Name:</b> {cust['name']}<br>
            <b>Balance:</b> {cust['balance']}<br>
            <b>Campaign Calls:</b> {cust['campaign']}<br>
            <b>Predicted Risk:</b> <b>{cust['risk']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(px.pie(df, names="risk", title="Customer Risk Distribution"), use_container_width=True)
        st.plotly_chart(px.scatter(df, x="campaign", y="balance", color="risk", title="Campaign vs Balance"), use_container_width=True)

# =================================================
# APP ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
