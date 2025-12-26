import streamlit as st
from auth import login_user, register_user
from utils import load_data
from models import segment_customers, predict_risk

st.set_page_config(
    page_title="AI Banking Intelligence",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ==================================================
# 🔐 LOGIN / REGISTER PAGE
# ==================================================
if st.session_state.page == "login":

    st.markdown("## 🔐 AI Banking Platform")
    choice = st.radio("Select Option", ["Login", "Register"], horizontal=True)

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

    # ---------- SIDEBAR ----------
    st.sidebar.success(f"Logged in as:\n{st.session_state.user_email}")

    if st.sidebar.button("Logout"):
        st.session_state.page = "login"
        st.session_state.user_email = None
        st.rerun()

    # ---------- LOAD DATA ----------
    df = load_data()

    # ---------- HEADER ----------
    st.markdown("## 🏦 AI Banking Intelligence Dashboard")
    st.caption("Customer Behavior Analysis using Machine Learning")

    # ---------- KPIs ----------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Total Customers", len(df))
    c2.metric("💰 Avg Balance", f"₹{int(df['balance'].mean()):,}")
    c3.metric("📞 Avg Campaigns", round(df["campaign"].mean(), 2))
    c4.metric(
        "📈 Subscription Rate",
        f"{round(df['y'].value_counts(normalize=True).get('yes', 0)*100, 2)}%"
    )

    st.divider()

    # ---------- DATA PREVIEW ----------
    st.subheader("📄 Customer Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.divider()

    # ---------- MACHINE LEARNING ----------
    st.subheader("🧠 Machine Learning Operations")

    df_ml = df.copy()
    df_ml["y"] = df_ml["y"].map({"yes": 1, "no": 0})

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Run Customer Segmentation"):
            seg = segment_customers(df_ml)
            st.success("Customer segmentation completed")
            st.dataframe(seg[["age", "balance", "segment"]].head())

    with col2:
        if st.button("Run Risk Prediction"):
            risk = predict_risk(df_ml)
            st.success("Risk prediction completed")
            st.bar_chart(risk["risk"].value_counts())

    st.divider()

    # ---------- AI INSIGHTS ----------
    st.subheader("🤖 AI Insights")

    high_risk_estimate = int(len(df) * 0.25)

    if high_risk_estimate > 1000:
        st.warning("⚠️ High churn risk detected. Retention strategies recommended.")
    else:
        st.success("✅ Customer base appears stable. Focus on upselling opportunities.")
