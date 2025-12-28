import streamlit as st
import pandas as pd
import plotly.express as px
import base64

from sklearn.linear_model import LogisticRegression
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
# LOAD DATASET
# =================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_data = load_data()

# =================================================
# TRAIN ML MODEL (LOGISTIC REGRESSION)
# =================================================
@st.cache_resource
def train_model(df):
    data = df.copy()
    encoders = {}

    for col in data.select_dtypes(include="object").columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])
        encoders[col] = le

    X = data.drop("y", axis=1)
    y = data["y"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    return model, X.columns

ml_model, feature_cols = train_model(bank_data)

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
# LOGIN PAGE
# =================================================
def login_page():
    st.markdown(
        """
        <div style="width:420px;margin:120px auto;
        background:#020617;padding:30px;border-radius:18px;
        color:white;text-align:center;">
        <h2>🏦 Customer Analysis Platform</h2>
        <p>ML-Powered Customer Intelligence</p>
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

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # -------------------------------------------------
    # DASHBOARD – HISTORICAL + LIVE ANALYSIS
    # -------------------------------------------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        st.info("Historical analysis based on bank marketing dataset")

        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>Subscription Rate</h3><h2>{(bank_data['y']=='yes').mean()*100:.2f}%</h2></div>", unsafe_allow_html=True)

        st.plotly_chart(
            px.histogram(bank_data, x="balance", title="Historical Balance Distribution"),
            use_container_width=True
        )

        # 🔥 LIVE CUSTOMER ANALYSIS (VISIBLE CHANGE)
        st.markdown("## 📊 Live Customer Analysis (Simulation)")

        if st.session_state.customers:
            live_df = pd.DataFrame(st.session_state.customers)

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    px.pie(live_df, names="risk", title="Live Risk Distribution"),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    px.histogram(live_df, x="balance", title="Live Balance Distribution"),
                    use_container_width=True
                )
        else:
            st.info("No live customers added yet")

    # -------------------------------------------------
    # ADD CUSTOMER
    # -------------------------------------------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        name = st.text_input("Customer Name")
        age = st.slider("Age", 18, 70)
        balance = st.number_input("Balance")
        campaign = st.slider("Campaign Calls", 1, 10)

        if st.button("Add Customer"):
            st.session_state.customers.append({
                "name": name,
                "age": age,
                "balance": balance,
                "campaign": campaign,
                "risk": "Pending"
            })
            st.success("Customer added")

    # -------------------------------------------------
    # VIEW + DELETE CUSTOMERS
    # -------------------------------------------------
    if menu == "View Customers":
        st.title("👥 View & Delete Customers")

        if not st.session_state.customers:
            st.info("No customers available")
            st.stop()

        df = pd.DataFrame(st.session_state.customers)
        st.dataframe(df, use_container_width=True)

        selected = st.multiselect("Select customers to delete", df["name"])
        if st.button("Delete Selected"):
            st.session_state.customers = [
                c for c in st.session_state.customers if c["name"] not in selected
            ]
            st.success("Deleted successfully")
            st.rerun()

    # -------------------------------------------------
    # ML PREDICTION (VISIBLE ML OUTPUT)
    # -------------------------------------------------
    if menu == "Prediction":
        st.title("🔮 ML-Based Risk Prediction")

        if not st.session_state.customers:
            st.warning("Please add customers first")
            st.stop()

        df = pd.DataFrame(st.session_state.customers)
        selected = st.selectbox("Select Customer", df["name"])
        cust = df[df["name"] == selected].iloc[0]

        input_df = pd.DataFrame([{
            "age": cust["age"],
            "balance": cust["balance"],
            "campaign": cust["campaign"]
        }])

        for col in feature_cols:
            if col not in input_df:
                input_df[col] = 0

        input_df = input_df[feature_cols]

        prob = ml_model.predict_proba(input_df)[0][1] * 100
        risk = "High Risk" if prob < 30 else "Medium Risk" if prob < 60 else "Low Risk"

        cust["risk"] = risk

        st.markdown(
            f"""
            <div style="background:#020617;padding:24px;border-radius:16px;color:white;">
            <h3>Prediction Result</h3>
            <b>Name:</b> {cust['name']}<br>
            <b>Probability of Subscription:</b> {prob:.2f}%<br>
            <b>Risk Level:</b> <span style="font-size:22px;font-weight:800;">{risk}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 🔥 ML PROBABILITY VISUAL (VISIBLE CHANGE)
        prob_df = pd.DataFrame({
            "Outcome": ["Not Subscribe", "Subscribe"],
            "Probability (%)": [100 - prob, prob]
        })

        st.plotly_chart(
            px.bar(
                prob_df,
                x="Outcome",
                y="Probability (%)",
                color="Outcome",
                text="Probability (%)",
                title="Logistic Regression Prediction Confidence"
            ),
            use_container_width=True
        )

# =================================================
# APP ROUTER
# =================================================
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
