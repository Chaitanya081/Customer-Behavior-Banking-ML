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
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # demo mode

if "customers" not in st.session_state:
    st.session_state.customers = []

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
        padding: 20px;
        border-radius: 14px;
        text-align: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Customer", "View Customers", "Prediction"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# -------------------------------------------------
# RISK LOGIC
# -------------------------------------------------
def calculate_risk(balance, campaign):
    if balance < 0 and campaign >= 3:
        return "High Risk"
    elif campaign >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
if menu == "Dashboard":
    st.title("📊 Customer Intelligence Dashboard")

    total = len(st.session_state.customers)

    if total == 0:
        st.info("No customers added yet.")
    else:
        df = pd.DataFrame(st.session_state.customers)

        high_risk_pct = round((df["risk"] == "High Risk").mean() * 100, 2)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>Total Customers</h3><h2>{total}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>High Risk (%)</h3><h2>{high_risk_pct}%</h2></div>", unsafe_allow_html=True)
        c3.markdown("<div class='card'><h3>Status</h3><h2>Live</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(df, names="risk", title="Risk Distribution")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(df, x="balance", nbins=20, title="Balance Distribution")
            st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# ADD CUSTOMER
# -------------------------------------------------
if menu == "Add Customer":
    st.title("➕ Add Customer")

    st.subheader("Add Single Customer")

    name = st.text_input("Customer Name")
    balance = st.number_input("Balance", value=0.0)
    campaign = st.number_input("Campaign Calls", min_value=0, step=1)

    if st.button("Add Customer"):
        risk = calculate_risk(balance, campaign)
        st.session_state.customers.append({
            "name": name,
            "balance": balance,
            "campaign": campaign,
            "risk": risk
        })
        st.success(f"Customer {name} added successfully")

    st.markdown("---")
    st.subheader("Add Multiple Customers (CSV)")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)

        for _, row in df.iterrows():
            risk = calculate_risk(row["balance"], row["campaign"])
            st.session_state.customers.append({
                "name": row["name"],
                "balance": row["balance"],
                "campaign": row["campaign"],
                "risk": risk
            })

        st.success("CSV customers added successfully")

# -------------------------------------------------
# VIEW & DELETE CUSTOMERS
# -------------------------------------------------
if menu == "View Customers":
    st.title("👥 View & Delete Customers")

    if not st.session_state.customers:
        st.info("No customers available")
    else:
        df = pd.DataFrame(st.session_state.customers)

        selected = st.multiselect(
            "Select customers to delete",
            df["name"].tolist()
        )

        if st.button("🗑 Delete Selected"):
            st.session_state.customers = [
                c for c in st.session_state.customers
                if c["name"] not in selected
            ]
            st.success("Selected customers deleted")
            st.experimental_rerun()

        if st.button("⚠ Delete ALL Customers"):
            st.session_state.customers.clear()
            st.warning("All customers deleted")
            st.experimental_rerun()

        st.dataframe(df, use_container_width=True)

# -------------------------------------------------
# PREDICTION
# -------------------------------------------------
if menu == "Prediction":
    st.title("🔮 Risk Prediction")

    if not st.session_state.customers:
        st.info("Add customers first")
    else:
        df = pd.DataFrame(st.session_state.customers)

        customer_name = st.selectbox("Select Customer", df["name"])

        customer = df[df["name"] == customer_name].iloc[0]

        st.markdown("### Customer Details")
        st.json(customer.to_dict())

        st.success(f"Predicted Risk: **{customer['risk']}**")
