import streamlit as st
import base64

def apply_login_style(image_path):
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img}");
            background-size: cover;
            background-position: center;
        }}

        .login-box {{
            background: rgba(0,0,0,0.75);
            padding: 30px;
            border-radius: 15px;
            width: 420px;
            margin: auto;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
