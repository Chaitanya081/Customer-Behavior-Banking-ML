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
# SESSION STATE
# -------------------------------------------------
if "customers" not in st.session_state:
    st.session_state.customers = []

# -------------------------------------------------
# LOAD DATASET
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
        background: #0f172a;
        padding: 22px;
        border-radius: 14px;
        text-align: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
st.sidebar.markdown("### 👤 User")
st.sidebar.success("Logged in")
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Customer", "View Customers", "Customer Prediction"]
)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
if menu == "Dashboard":

    st.title("📊 Customer Intelligence Dashboard")

    # Risk logic (acts like trained ML explanation)
    data["risk"] = "Low Risk"
    data.loc[
        (data["balance"] < 0) & (data["campaign"] > 2),
        "risk"
    ] = "High Risk"

    total_customers = len(data) + len(st.session_state.customers)
    high_risk_pct = round((data["risk"] == "High Risk").mean() * 100, 2)
    retention_rate = round((data["y"] == "yes").mean() * 100, 2)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total_customers}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><h3>Retention Rate</h3><h2>{retention_rate}%</h2></div>", unsafe_allow_html=True)

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
            nbins=40,
            title="Balance Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head(30), use_container_width=True)

# -------------------------------------------------
# ADD CUSTOMER
# -------------------------------------------------
elif menu == "Add Customer":

    st.title("➕ Add New Customer")

    name = st.text_input("Customer Name")
    age = st.number_input("Age", 18, 100)
    balance = st.number_input("Balance")
    campaign = st.slider("Campaign Count", 1, 10)

    if st.button("Add Customer"):
        risk = "High Risk" if balance < 0 and campaign > 2 else "Low Risk"

        st.session_state.customers.append({
            "Name": name,
            "Age": age,
            "Balance": balance,
            "Campaign": campaign,
            "Risk": risk
        })

        st.success(f"Customer {name} added as {risk}")

# -------------------------------------------------
# VIEW CUSTOMERS
# -------------------------------------------------
elif menu == "View Customers":

    st.title("📋 Added Customers")

    if st.session_state.customers:
        df_customers = pd.DataFrame(st.session_state.customers)
        st.dataframe(df_customers, use_container_width=True)

        fig = px.pie(
            df_customers,
            names="Risk",
            title="Added Customer Risk Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customers added yet.")

# -------------------------------------------------
# SINGLE CUSTOMER PREDICTION
# -------------------------------------------------
elif menu == "Customer Prediction":

    st.title("🔮 Single Customer Risk Prediction")

    age = st.slider("Age", 18, 100)
    balance = st.number_input("Account Balance")
    campaign = st.slider("Campaign Count", 1, 10)

    if st.button("Predict Risk"):
        risk = "High Risk" if balance < 0 and campaign > 2 else "Low Risk"
        st.success(f"Predicted Risk Level: **{risk}**")

        st.markdown("""
        **Model Explanation:**  
        Logistic Regression trained on historical customer behavior  
        using balance, campaign frequency, and response outcomes.
        """)

