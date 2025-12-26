import streamlit as st
import matplotlib.pyplot as plt
from auth import login_user, register_user
from utils import load_data
from models import segment_customers, predict_risk_single

st.set_page_config(layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- LOGIN ----------------
if st.session_state.page == "login":
    st.title("🔐 AI Banking Platform")
    option = st.radio("Select Option", ["Login", "Register"], horizontal=True)

    if option == "Login":
        login_user()
    else:
        register_user()

# ---------------- DASHBOARD ----------------
elif st.session_state.page == "dashboard":

    df = load_data()

    st.sidebar.success(f"Logged in as\n{st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.page = "login"
        st.rerun()

    st.title("🏦 AI Banking Intelligence Dashboard")

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", len(df))
    c2.metric("Avg Balance", int(df["balance"].mean()))
    c3.metric("Subscribed %",
              round(df["y"].value_counts(normalize=True)["yes"] * 100, 2))

    st.divider()

    # Charts
    st.subheader("📊 Customer Analysis")

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        df["job"].value_counts().head(6).plot(kind="bar", ax=ax)
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots()
        df["y"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
        st.pyplot(fig2)

    st.divider()

    # Segmentation
    st.subheader("🧠 Customer Segmentation")
    if st.button("Run Customer Segmentation"):
        seg = segment_customers(df.copy())
        st.dataframe(seg[["age", "balance", "segment"]].head(20))

    st.divider()

    # User Prediction
    st.subheader("🔮 Predict Risk for New Customer")

    col1, col2, col3, col4 = st.columns(4)
    age = col1.number_input("Age", 18, 100, 30)
    balance = col2.number_input("Balance", -50000, 1000000, 5000)
    duration = col3.number_input("Call Duration (sec)", 0, 5000, 120)
    campaign = col4.number_input("Campaign Contacts", 1, 20, 2)

    if st.button("Predict Customer Risk"):
        risk = predict_risk_single(age, balance, duration, campaign)
        if risk == "High Risk":
            st.error(f"⚠️ {risk}")
        elif risk == "Medium Risk":
            st.warning(f"⚠️ {risk}")
        else:
            st.success(f"✅ {risk}")
