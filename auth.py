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

def set_background():
    image_path = "images/loginimage.jpg"

    if not os.path.exists(image_path):
        st.error("❌ loginimage.jpg not found inside images folder")
        return

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .login-box {{
            background: rgba(0, 0, 0, 0.65);
            padding: 30px;
            border-radius: 15px;
            width: 400px;
            margin: auto;
            margin-top: 120px;
        }}

        label, h2 {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def register_user():
    init_user_db()
    set_background()

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
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

    st.markdown("</div>", unsafe_allow_html=True)

def login_user():
    init_user_db()
    set_background()

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login")

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
            st.error("Invalid email or password")

    st.markdown("</div>", unsafe_allow_html=True)
