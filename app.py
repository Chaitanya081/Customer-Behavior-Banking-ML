import streamlit as st
import os
from styles import apply_login_style
from auth import register_user, login_user

st.set_page_config(page_title="AI Banking Platform", layout="wide")

# ✅ HARD INITIALIZATION (THIS FIXES EVERYTHING)
if "users" not in st.session_state:
    st.session_state["users"] = {}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

IMAGE_PATH = os.path.join(os.getcwd(), "images", "loginimage.jpg")

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state["logged_in"]:
    apply_login_style(IMAGE_PATH)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🔐 AI Banking Platform")

    option = st.radio("Select Option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Register"):
            if register_user(email, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("User already exists")

    else:
        if st.button("Login"):
            if login_user(email, password):
                st.session_state["logged_in"] = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid email or password")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
else:
    st.sidebar.success("Logged in")

    st.title("🏦 AI Banking Intelligence Dashboard")
    st.write("Welcome! You are inside the application.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", "45,211")
    col2.metric("High Risk", "12%")
    col3.metric("Retention Rate", "88%")

    st.subheader("📊 Customer Insights")
    st.bar_chart([20, 35, 15, 30])

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()
