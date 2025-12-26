import streamlit as st
import pandas as pd
import os

USER_FILE = "data/users.csv"

def init_user_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["email", "password"]).to_csv(USER_FILE, index=False)

def login_user():
    init_user_db()

    # ✅ THIS ALWAYS WORKS
    st.image("images/loginimage.jpg", use_column_width=True)

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

def register_user():
    init_user_db()

    st.image("images/loginimage.jpg", use_column_width=True)

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
