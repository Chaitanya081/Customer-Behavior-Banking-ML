import streamlit as st
import pandas as pd
import os
import base64

USER_FILE = "data/users.csv"

# ---------- Initialize user DB ----------
def init_user_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["email", "password"]).to_csv(USER_FILE, index=False)

# ---------- Background image ----------
def load_bg_image():
    with open("images/loginimage.jpg", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
    }}
    .auth-card {{
        background: rgba(255,255,255,0.75);
        padding: 35px;
        border-radius: 15px;
        width: 420px;
        margin: auto;
        margin-top: 120px;
        box-shadow: 0 0 25px rgba(0,0,0,0.5);
    }}
    label {{
        color: black !important;
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------- REGISTER ----------
def register():
    init_user_db()
    load_bg_image()

    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("## 📝 Register")

    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not email or not password:
            st.error("All fields required")
        elif password != confirm:
            st.error("Passwords do not match")
        else:
            df = pd.read_csv(USER_FILE)
            if email in df["email"].values:
                st.error("Email already registered")
            else:
                df.loc[len(df)] = [email, password]
                df.to_csv(USER_FILE, index=False)
                st.success("Registration successful! Please login.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- LOGIN ----------
def login():
    init_user_db()
    load_bg_image()

    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Sign In")

    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        df = pd.read_csv(USER_FILE)
        valid = ((df["email"] == email) & (df["password"] == password)).any()

        if valid:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Login successful")
        else:
            st.error("Invalid email or password")

    st.markdown("</div>", unsafe_allow_html=True)
