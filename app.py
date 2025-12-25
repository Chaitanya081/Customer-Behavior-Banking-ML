import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from login import login_page
from styles import apply_style
from utils import load_data, encode
from model import segment_customers, predict_risk

st.set_page_config(page_title="AI Banking Intelligence", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

apply_style()

if not st.session_state.logged_in:
    login_page()
    st.stop()

# SIDEBAR
st.sidebar.image("images/logo.png", use_column_width=True)
st.sidebar.markdown("### Filters")

df = load_data()

job = st.sidebar.multiselect("Job", df["job"].unique())
marital = st.sidebar.multiselect("Marital", df["marital"].unique())

if job:
    df = df[df["job"].isin(job)]
if marital:
    df = df[df["marital"].isin(marital)]

# HEADER
st.image("images/dashboard_banner.png", use_column_width=True)

st.markdown("""
## 🏦 AI-Powered Banking Intelligence Platform  
**Customer Insights • Risk Prediction • Smart Decisions**
""")

# KPIs
c1, c2, c3, c4 = st.columns(4)

c1.metric("👥 Customers", len(df))
c2.metric("💰 Avg Balance", f"₹{int(df['balance'].mean()):,}")
c3.metric("📞 Avg Campaigns", round(df["campaign"].mean(),2))
c4.metric("📈 Subscription Rate", f"{round(df['y'].value_counts(normalize=True)[1]*100,2)}%")

st.markdown("---")

# VISUALS
left, right = st.columns(2)

with left:
    st.markdown("### Customers by Job")
    fig, ax = plt.subplots()
    df["job"].value_counts().head(6).plot(kind="line", ax=ax, marker="o")
    st.pyplot(fig)

with right:
    st.markdown("### Balance by Marital Status")
    fig2, ax2 = plt.subplots()
    sns.barplot(x=df["marital"], y=df["balance"], ax=ax2)
    st.pyplot(fig2)

# ML SECTION
st.markdown("---")
st.markdown("## 🧠 AI Analysis")

df_enc = encode(df.copy())

if st.button("Run Customer Segmentation"):
    df_seg = segment_customers(df_enc)
    st.success("Customer Segmentation Completed")
    st.dataframe(df_seg[["age","balance","segment"]].head())

if st.button("Run Risk Prediction"):
    df_risk = predict_risk(df_enc)
    st.success("Risk Prediction Completed")
    st.bar_chart(df_risk["risk"].value_counts())

    high_risk = df_risk[df_risk["risk"]=="High"].shape[0]

    st.markdown("## 🤖 AI Recommendation")
    if high_risk > 1000:
        st.warning("⚠️ High churn risk detected. Launch retention campaigns.")
    else:
        st.success("✅ Customer base stable. Focus on upselling.")
