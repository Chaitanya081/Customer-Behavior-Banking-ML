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
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------------------------------
# LOAD DATASET (NO ASSUMPTIONS)
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/bank_marketing.csv",
        sep=";",
        engine="python",
        dtype=str   # read EVERYTHING as string first
    )

    # Clean column names brutally
    df.columns = (
        df.columns
        .astype(str)
        .str.replace('"', '', regex=False)
        .str.strip()
        .str.lower()
    )

    return df

data = load_data()

# -------------------------------------------------
# DEBUG: SHOW REAL COLUMNS (REMOVE LATER)
# -------------------------------------------------
st.write("🔍 Detected columns:", data.columns.tolist())

# -------------------------------------------------
# COLUMN MAPPING (THIS IS THE FIX)
# -------------------------------------------------
def find_column(possible_names):
    for col in data.columns:
        for name in possible_names:
            if name in col:
                return col
    return None

balance_col = find_column(["balance"])
campaign_col = find_column(["campaign"])
target_col = find_column(["y"])

# -------------------------------------------------
# IF STILL NOT FOUND → STOP GRACEFULLY
# -------------------------------------------------
if not balance_col or not campaign_col or not target_col:
    st.error("❌ Required columns not found in dataset")
    st.write("Detected columns:", data.columns.tolist())
    st.stop()

# Convert required columns safely
data[balance_col] = pd.to_numeric(data[balance_col], errors="coerce").fillna(0)
data[campaign_col] = pd.to_numeric(data[campaign_col], errors="coerce").fillna(0)

# -------------------------------------------------
# BACKGROUND IMAGE (OPTIONAL)
# -------------------------------------------------
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
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
        </style>
        """,
        unsafe_allow_html=True
    )
except:
    pass

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
def dashboard():

    st.title("📊 Customer Intelligence Dashboard")

    # SAFE RISK LOGIC (USING MAPPED COLUMNS)
    data["risk"] = "Low Risk"
    data.loc[
        (data[balance_col] < 0) & (data[campaign_col] > 2),
        "risk"
    ] = "High Risk"

    total_customers = len(data)
    high_risk_pct = round((data["risk"] == "High Risk").mean() * 100, 2)
    retention_rate = round((data[target_col] == "yes").mean() * 100, 2)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", total_customers)
    c2.metric("High Risk (%)", high_risk_pct)
    c3.metric("Retention Rate (%)", retention_rate)

    fig = px.pie(data, names="risk", title="Customer Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Dataset Preview")
    st.dataframe(data.head(20), use_container_width=True)

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
dashboard()
