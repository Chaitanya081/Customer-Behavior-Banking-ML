import streamlit as st
import base64
import os

def login_page():

    # ---------- Load background image ----------
    img_path = "images/loginimage.jpg"

    if not os.path.exists(img_path):
        st.error("Login background image not found")
        return

    with open(img_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    # ---------- CSS for background + overlay ----------
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .login-card {{
            background: rgba(0, 0, 0, 0.65);
            padding: 35px;
            border-radius: 15px;
            width: 380px;
            margin: auto;
            margin-top: 120px;
            box-shadow: 0 0 25px rgba(0,0,0,0.7);
        }}

        .login-title {{
            text-align: center;
            color: white;
            font-size: 26px;
            font-weight: 600;
            margin-bottom: 25px;
        }}

        label {{
            color: white !important;
        }}

        input {{
            background-color: #0f1f2e !important;
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------- Login UI ----------
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 AI Banking Platform Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)
