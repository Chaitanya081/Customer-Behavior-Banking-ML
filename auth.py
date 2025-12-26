import streamlit as st

def init_users():
    if "users" not in st.session_state:
        st.session_state.users = {}

def register_user(email, password):
    init_users()
    if email in st.session_state.users:
        return False
    st.session_state.users[email] = password
    return True

def login_user(email, password):
    init_users()
    return st.session_state.users.get(email) == password
