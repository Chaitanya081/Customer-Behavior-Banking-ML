import streamlit as st
import pandas as pd
import os

USER_FILE = "data/users.csv"

def init_user_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["email", "password"]).to_csv(USER_FILE, index=False)


def register_user():
    init_user_db()
    st.subheader("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        df = pd.read_csv(USER_FILE)
        if email in df["email"].values:
            st.error("Email already exists")
        else:
            df.loc[len(df)] = [email, password]
            df.to_csv(USER_FILE, index=False)
            st.success("Registration successful. Please login.")


def login_user():
    init_user_db()
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        df = pd.read_csv(USER_FILE)
        valid = ((df["email"] == email) & (df["password"] == password)).any()

        if valid:
            st.session_state.user_email = email
            st.success("Login successful")
            return True
        else:
            st.error("Invalid credentials")

    return False
