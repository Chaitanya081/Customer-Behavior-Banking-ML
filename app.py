import streamlit as st
from auth import register, login
from styles import apply_style
from utils import load_data
from models import segment_customers, predict_risk

st.set_page_config(page_title="AI Banking Platform", layout="wide")

# ---------------- SESSION STATE INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- AUTH SECTION ----------------
if not st.session_state.logged_in:
    choice = st.radio("", ["Login", "Register"], horizontal=True)

    if choice == "Register":
        register()
    else:
        login()

    # ⛔ STOP ONLY WHEN NOT LOGGED IN
    st.stop()

# ================= DASHBOARD STARTS HERE =================

apply_style()

st.sidebar.success(f"Logged in as {st.session_state.user_email}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- LOAD DATA ----------------
df = load_data()

st.title("🏦 AI Banking Intelligence Dashboard")
st.caption("Customer Behavior • Risk Prediction • Smart Decisions")

# ---------------- KPIs ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Customers", len(df))
c2.metric("💰 Avg Balance", f"₹{int(df['balance'].mean()):,}")
c3.metric("📞 Avg Campaigns", round(df["campaign"].mean(), 2))
c4.metric(
    "📈 Subscription Rate",
    f"{round(df['y'].value_counts(normalize=True).get('yes', 0)*100, 2)}%"
)

st.divider()

# ---------------- ML OPERATIONS ----------------
st.subheader("🧠 AI Operations")

df_encoded = df.copy()
df_encoded["y"] = df_encoded["y"].map({"yes": 1, "no": 0})

if st.button("Run Customer Segmentation"):
    df_seg = segment_customers(df_encoded)
    st.success("Customer segmentation completed")
    st.dataframe(df_seg[["age", "balance", "segment"]].head())

if st.button("Run Risk Prediction"):
    df_risk = predict_risk(df_encoded)
    st.success("Risk prediction completed")
    st.bar_chart(df_risk["risk"].value_counts())

    high_risk = df_risk[df_risk["risk"] == "High"].shape[0]
    st.subheader("🤖 AI Recommendation")

    if high_risk > 1000:
        st.warning("High churn risk detected. Launch retention campaigns.")
    else:
        st.success("Customer base stable. Focus on upselling.")
