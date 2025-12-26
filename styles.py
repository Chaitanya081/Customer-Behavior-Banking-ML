import streamlit as st

def apply_login_style(image_path):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_path}");
            background-size: cover;
            background-position: center;
        }}
        .login-box {{
            background: rgba(0,0,0,0.65);
            padding: 30px;
            border-radius: 12px;
            width: 400px;
            margin: auto;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
