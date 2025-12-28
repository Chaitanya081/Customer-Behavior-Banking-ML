import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import base64
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# =================================================
# CONFIG
# =================================================
st.set_page_config("Customer Analysis Platform", layout="wide")

DB = "bank.db"

# =================================================
# DATABASE
# =================================================
conn = sqlite3.connect(DB, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    email TEXT PRIMARY KEY,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS customers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    balance REAL,
    campaign INTEGER,
    risk TEXT
)
""")
conn.commit()

# =================================================
# LOAD DATASET & TRAIN ML
# =================================================
@st.cache_data
def train_model():
    df = pd.read_csv("data/bank_marketing.csv", sep=";")
    df = df[["age", "balance", "campaign", "y"]]
    df["risk"] = df["y"].map({"yes": 0, "no": 1})

    X = df[["age", "balance", "campaign"]]
    y = df["risk"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model

model = train_model()

# =================================================
# RISK LOGIC (ML + RULE HYBRID)
# =================================================
def predict_risk(age, balance, campaign):
    pred = model.predict([[age, balance, campaign]])[0]
    if pred == 1 and campaign >= 4:
        return "High Risk"
    elif campaign >= 2:
        return "Medium Risk"
    return "Low Risk"

# =================================================
# PDF REPORT
# =================================================
def generate_pdf(customer):
    filename = f"report_{customer['name']}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Customer Risk Analysis Report")

    c.setFont("Helvetica", 12)
    y = 760
    for k, v in customer.items():
        c.drawString(50, y, f"{k.capitalize()}: {v}")
        y -= 30

    c.drawString(50, y-20, f"Generated on: {datetime.now()}")
    c.save()

    return filename

# =================================================
# LOGIN
# =================================================
def login_page():
    st.title("🏦 Customer Analysis Platform")
    option = st.radio("Select", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button(option):
        if option == "Register":
            cur.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (email, password))
            conn.commit()
            st.success("Registered")
        else:
            cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            if cur.fetchone():
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Invalid login")

# =================================================
# DASHBOARD
# =================================================
def dashboard():
    menu = st.sidebar.radio("Navigation", [
        "Dashboard",
        "Add Customers",
        "View Customers",
        "Prediction",
        "Admin Analytics"
    ])

    # DASHBOARD
    if menu == "Dashboard":
        st.title("📊 Dashboard")

        df = pd.read_sql("SELECT * FROM customers", conn)
        if df.empty:
            st.info("No data yet")
            return

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", len(df))
        col2.metric("High Risk %", round((df["risk"]=="High Risk").mean()*100,2))
        col3.metric("Avg Balance", round(df["balance"].mean(),2))

        st.plotly_chart(px.pie(df, names="risk"), use_container_width=True)

    # ADD
    if menu == "Add Customers":
        st.title("➕ Add Customers")

        mode = st.radio("Mode", ["Single", "CSV Upload"])

        if mode == "Single":
            name = st.text_input("Name")
            age = st.number_input("Age", 18, 100)
            balance = st.number_input("Balance")
            campaign = st.slider("Campaign Calls", 1, 10)

            if st.button("Add"):
                risk = predict_risk(age, balance, campaign)
                cur.execute(
                    "INSERT INTO customers(name,age,balance,campaign,risk) VALUES(?,?,?,?,?)",
                    (name, age, balance, campaign, risk)
                )
                conn.commit()
                st.success("Customer added")

        else:
            file = st.file_uploader("CSV (name,age,balance,campaign)", type="csv")
            if file:
                df = pd.read_csv(file)
                for _, r in df.iterrows():
                    risk = predict_risk(r["age"], r["balance"], r["campaign"])
                    cur.execute(
                        "INSERT INTO customers(name,age,balance,campaign,risk) VALUES(?,?,?,?,?)",
                        (r["name"], r["age"], r["balance"], r["campaign"], risk)
                    )
                conn.commit()
                st.success("Bulk upload done")

    # VIEW
    if menu == "View Customers":
        st.title("👥 Customers")
        df = pd.read_sql("SELECT * FROM customers", conn)
        st.dataframe(df)

        ids = st.multiselect("Delete by ID", df["id"].tolist())
        if st.button("Delete Selected"):
            for i in ids:
                cur.execute("DELETE FROM customers WHERE id=?", (i,))
            conn.commit()
            st.rerun()

    # PREDICTION
    if menu == "Prediction":
        st.title("🔮 Prediction")

        df = pd.read_sql("SELECT * FROM customers", conn)
        sel = st.selectbox("Select", df["name"])
        cust = df[df["name"]==sel].iloc[0]

        st.json(cust.to_dict())

        pdf = generate_pdf(cust.to_dict())
        with open(pdf, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name=pdf)

        st.plotly_chart(px.scatter(df, x="campaign", y="balance", color="risk"))

    # ADMIN
    if menu == "Admin Analytics":
        st.title("🧠 Admin Analytics")

        df = pd.read_sql("SELECT * FROM customers", conn)

        st.subheader("High Risk Customers")
        st.dataframe(df[df["risk"]=="High Risk"])

        st.subheader("Risk vs Campaign")
        st.plotly_chart(px.box(df, x="risk", y="campaign"), use_container_width=True)

# =================================================
# ROUTER
# =================================================
if "user" not in st.session_state:
    login_page()
else:
    dashboard()
