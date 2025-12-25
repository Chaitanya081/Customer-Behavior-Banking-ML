import streamlit as st

def login_page():
    st.image("images/login_banner.png", use_column_width=True)
    st.markdown("## 🔐 AI Banking Platform Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")
