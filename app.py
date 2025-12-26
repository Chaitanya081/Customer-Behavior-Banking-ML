import streamlit as st
from auth import login_user, register_user
from utils import load_data
from models import segment_customers, predict_risk

st.set_page_config(page_title="AI Banking Platform", layout="wide")

# ---------- SESSION STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ==================================================
# 🔐 LOGIN / REGISTER PAGE
# ==================================================
if st.session_state.page == "login":

    choice = st.radio("Choose option", ["Login", "Register"], horizontal=True)

    if choice == "Login":
        success = login_user()
        if success:
            st.session_state.page = "dashboard"
            st.rerun()

    else:
        register_user()

# ==================================================
# 🏦 DASHBOARD PAGE
# ==================================================
elif st.session_state.page == "dashboard":

    st.sidebar.success(f"Logged in as {st.session_state.user_email}")

    if st.sidebar.button("Logout"):
        st.session_state.page = "login"
        st.session_state.user_email = None
        st.rerun()

    st.title("🏦 AI Banking Intelligence Dashboard")

    df = load_data()

    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", len(df))
    c2.metric("Avg Balance", int(df["balance"].mean()))
    c3.metric("Avg Campaign", round(df["campaign"].mean(), 2))

    st.divider()

    df["y"] = df["y"].map({"yes": 1, "no": 0})

    if st.button("Run Customer Segmentation"):
        seg = segment_customers(df.copy())
        st.dataframe(seg.head())

    if st.button("Run Risk Prediction"):
        risk = predict_risk(df.copy())
        st.write(risk["risk"].value_counts())
