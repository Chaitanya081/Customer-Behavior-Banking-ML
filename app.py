import streamlit as st
import matplotlib.pyplot as plt
from utils import load_data, prepare_ml_data
from models import segment_customers, predict_risk
from auth import login_user, register_user

st.set_page_config(layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- LOGIN ----------------
if st.session_state.page == "login":
    option = st.radio("", ["Login", "Register"], horizontal=True)
    if option == "Login":
        login_user()
    else:
        register_user()

# ---------------- DASHBOARD ----------------
elif st.session_state.page == "dashboard":

    df = load_data()

    st.sidebar.success(f"Logged in as {st.session_state.user_email}")
    if st.sidebar.button("Logout"):
        st.session_state.page = "login"
        st.rerun()

    st.title("🏦 AI Banking Intelligence Dashboard")

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", len(df))
    c2.metric("Avg Balance", int(df["balance"].mean()))
    c3.metric("Subscribed %", round(df["y"].value_counts(normalize=True)["yes"]*100, 2))

    st.divider()

    # BAR CHART
    st.subheader("📊 Job Distribution")
    fig, ax = plt.subplots()
    df["job"].value_counts().head(8).plot(kind="bar", ax=ax)
    st.pyplot(fig)

    # PIE CHART
    st.subheader("🥧 Subscription Ratio")
    fig2, ax2 = plt.subplots()
    df["y"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
    st.pyplot(fig2)

    st.divider()

    # ML
    st.subheader("🧠 Machine Learning")

    if st.button("Run Customer Segmentation"):
        seg = segment_customers(df.copy())
        st.dataframe(seg[["age", "balance", "segment"]].head())

    if st.button("Run Risk Prediction"):
        X, y = prepare_ml_data(df)
        risk = predict_risk(X, y)
        st.bar_chart(pd.Series(risk).value_counts())
