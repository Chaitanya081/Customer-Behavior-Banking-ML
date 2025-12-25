import streamlit as st
import os

def login_page():
    img_path = "images/loginimage.jpg"   # ✅ correct file name

    if os.path.exists(img_path):
        st.image(img_path, use_column_width=True)
    else:
        st.warning("Login image not found")

    st.markdown("## 🔐 AI Banking Platform Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")
