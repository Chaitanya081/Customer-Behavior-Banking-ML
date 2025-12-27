import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Customer Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# SESSION STATE INIT
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
# LOAD DATASET (BANK MARKETING)
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        quotechar='"',
        engine="python"
    )
    df.columns = df.columns.str.strip().str.lower()
    return df

data = load_data()

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
        background-position: center;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.65);
        z-index: -1;
    }}
    .card {{
        background:#020617;
        padding:22px;
        border-radius:14px;
        text-align:center;
        color:white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOGIN / REGISTER PAGE
# -------------------------------------------------
def login_page():
    st.markdown(
        """
        <div style="
            width:420px;
            margin:120px auto;
            padding:30px;
            background:#020617;
            border-radius:18px;
            text-align:center;
            color:white;
        ">
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
                st.error("User already exists")
            else:
                st.session_state.users[email] = password
                st.success("Registered successfully. Please login.")

    if option == "Login":
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def dashboard():

    st.sidebar.markdown("### 👤 User")
    st.sidebar.success("Logged in")
    st.sidebar.write(st.session_state.current_user)

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Add Customer", "View Customers", "Prediction"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # -------------------------------------------------
    # DASHBOARD HOME
    # -------------------------------------------------
    if menu == "Dashboard":
        st.title("📊 Customer Intelligence Dashboard")

        # Risk logic on dataset
        data["risk"] = "Low Risk"
        data.loc[
            (data["balance"] < 0) | ((data["balance"] < 5000) & (data["campaign"] > 3)),
            "risk"
        ] = "High Risk"

        total = len(data)
        high_risk_pct = round((data["risk"] == "High Risk").mean() * 100, 2)
        retention = round((data["y"] == "yes").mean() * 100, 2)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention}%</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(
                data,
                names="risk",
                title="Customer Risk Distribution",
                color="risk",
                color_discrete_map={"High Risk": "#ef4444", "Low Risk": "#22c55e"}
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(
                data,
                x="balance",
                title="Balance Distribution",
                nbins=40
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Dataset Preview")
        st.dataframe(data.head(20), use_container_width=True)

    # -------------------------------------------------
    # ADD CUSTOMER
    # -------------------------------------------------
    if menu == "Add Customer":
        st.title("➕ Add Customer")

        name = st.text_input("Customer Name")
        balance = st.number_input("Balance", value=0.0)
        campaign = st.slider("Campaign Calls", 1, 10)

        if st.button("Add"):
            st.session_state.customers.append({
                "name": name,
                "balance": balance,
                "campaign": campaign
            })
            st.success(f"Customer {name} added")

    # -------------------------------------------------
    # VIEW CUSTOMERS
    # -------------------------------------------------
    if menu == "View Customers":
        st.title("👥 Known Customers")

        if st.session_state.customers:
            df = pd.DataFrame(st.session_state.customers)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No customers added yet")

    # -------------------------------------------------
    # SINGLE CUSTOMER PREDICTION
    # -------------------------------------------------
    if menu == "Prediction":
        st.title("🔮 Risk Prediction")

        cname = st.text_input("Customer Name")
        balance = st.number_input("Account Balance", value=0.0)
        campaign = st.slider("Campaign Calls", 1, 10)

        if st.button("Predict"):
            if balance < 0:
                risk = "High Risk"
                color = "#ef4444"
            elif balance < 5000 and campaign > 3:
                risk = "High Risk"
                color = "#ef4444"
            elif campaign > 6:
                risk = "Medium Risk"
                color = "#facc15"
            else:
                risk = "Low Risk"
                color = "#22c55e"

            st.markdown(
                f"""
                <div style="
                    background:#020617;
                    padding:24px;
                    border-radius:16px;
                    color:white;
                    font-size:18px;
                ">
                👤 <b>Customer:</b> {cname}<br><br>
                ⚠️ <b>Predicted Risk:</b>
                <span style="color:{color}; font-weight:700;">
                    {risk}
                </span>
                </div>
                """,
                unsafe_allow_html=True
            )

# -------------------------------------------------
# APP ROUTER
# -------------------------------------------------
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
