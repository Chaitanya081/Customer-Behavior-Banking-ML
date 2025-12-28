import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from sklearn.linear_model import LogisticRegression

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide"
)

# -------------------------------------------------
# SESSION STATE
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
# LOAD SAMPLE BANK DATA (DASHBOARD)
# -------------------------------------------------
@st.cache_data
def load_bank_data():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df.columns = df.columns.str.lower()
    return df

bank_data = load_bank_data()

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
        padding:20px;
        border-radius:14px;
        color:white;
        text-align:center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------
def login_page():
    st.markdown("<h2 style='text-align:center'>🏦 Customer Analysis Platform</h2>", unsafe_allow_html=True)

    option = st.radio("Select", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if email not in st.session_state.users:
                st.session_state.users[email] = password
                st.success("Registered successfully. Login now.")
            else:
                st.warning("User already exists. Please login.")

    if option == "Login":
        if st.button("Login"):
            if st.session_state.users.get(email) == password:
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("Invalid credentials")

# -------------------------------------------------
# RISK LOGIC
# -------------------------------------------------
def rule_based_risk(balance, campaign):
    if balance < 0 or campaign >= 6:
        return "High Risk"
    elif balance < 5000 and campaign >= 3:
        return "Medium Risk"
    return "Low Risk"

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
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
            lambda x: rule_based_risk(x["balance"], x["campaign"]),
            axis=1
        )

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{len(bank_data)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk</h3><h2>{(bank_data['risk']=='High Risk').mean()*100:.1f}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention</h3><h2>{(bank_data['y']=='yes').mean()*100:.1f}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(px.pie(bank_data, names="risk", title="Risk Distribution"), use_container_width=True)
        col2.plotly_chart(px.histogram(bank_data, x="balance", title="Balance Distribution"), use_container_width=True)

        st.subheader("📋 Sample Dataset (First 50 Rows)")
        st.dataframe(bank_data.head(50), use_container_width=True)

    # ---------------- ADD CUSTOMER ----------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        mode = st.radio("Mode", ["Single", "CSV Upload"])

        if mode == "Single":
            name = st.text_input("Name")
            balance = st.number_input("Balance", value=0.0)
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add"):
                st.session_state.customers.append({
                    "name": name,
                    "balance": balance,
                    "campaign": campaign,
                    "risk": rule_based_risk(balance, campaign)
                })
                st.success("Customer added")

        else:
            file = st.file_uploader("Upload CSV (name,balance,campaign)", type=["csv"])
            if file:
                df = pd.read_csv(file)
                df.columns = df.columns.str.lower()
                for _, r in df.iterrows():
                    st.session_state.customers.append({
                        "name": r["name"],
                        "balance": r["balance"],
                        "campaign": r["campaign"],
                        "risk": rule_based_risk(r["balance"], r["campaign"])
                    })
                st.success(f"{len(df)} customers added")

    # ---------------- VIEW + DELETE ----------------
    if menu == "View Customers":
        st.title("👥 Customers")

        if not st.session_state.customers:
            st.info("No customers added")
            return

        df = pd.DataFrame(st.session_state.customers)
        st.dataframe(df, use_container_width=True)

        selected = st.multiselect("Delete customers", df["name"].tolist())

        col1, col2 = st.columns(2)
        if col1.button("Delete Selected"):
            st.session_state.customers = [c for c in st.session_state.customers if c["name"] not in selected]
            st.success("Deleted")
            st.rerun()

        if col2.button("Delete ALL"):
            st.session_state.customers.clear()
            st.warning("All deleted")
            st.rerun()

    # ---------------- ML PREDICTION ----------------
    if menu == "Prediction":
        st.title("🤖 ML-Based Risk Prediction")

        if len(st.session_state.customers) < 5:
            st.warning("Add at least 5 customers for ML prediction")
            return

        df = pd.DataFrame(st.session_state.customers)

        X = df[["balance", "campaign"]]
        y = df["risk"].map({"Low Risk": 0, "Medium Risk": 1, "High Risk": 2})

        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)

        df["ml_risk"] = model.predict(X).map({0:"Low Risk",1:"Medium Risk",2:"High Risk"})

        st.plotly_chart(px.scatter(
            df, x="campaign", y="balance", color="ml_risk",
            hover_data=["name"], title="ML Risk Prediction"
        ), use_container_width=True)

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
