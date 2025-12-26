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

    # Load background image
    with open("images/loginimage.jpg", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}

        .login-card {{
            background: rgba(0,0,0,0.65);
            padding: 30px;
            border-radius: 12px;
            width: 380px;
            margin: auto;
            margin-top: 150px;
        }}

        h2, label {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

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

def register_user():
    init_user_db()

    st.markdown("## 📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        df = pd.read_csv(USER_FILE)
        if email in df["email"].values:
            st.error("User already exists")
        else:
            df.loc[len(df)] = [email, password]
            df.to_csv(USER_FILE, index=False)
            st.success("Registration successful. Please login.")
