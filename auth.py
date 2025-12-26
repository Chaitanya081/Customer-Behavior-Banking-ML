import streamlit as st
import pandas as pd
import os
import base64

USER_FILE = "data/users.csv"

def init_user_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["email", "password"]).to_csv(USER_FILE, index=False)

def login_user():
    init_user_db()

    # ---- Load image as base64 ----
    with open("images/loginimage.jpg", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    # ---- Background + Card CSS ----
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}

        .login-card {{
            background: rgba(0, 0, 0, 0.65);
            padding: 30px;
            border-radius: 12px;
            width: 380px;
            margin: auto;
            margin-top: 150px;
            box-shadow: 0px 0px 30px rgba(0,0,0,0.4);
        }}

        h2, label {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---- Login Card ----
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 AI Banking Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        df = pd.read_csv(USER_FILE)
        valid = ((df["email"] == email) & (df["password"] == password)).any()
        if valid:
            st.session_state.page = "dashboard"
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)
