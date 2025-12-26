import streamlit as st
import hashlib

def init_users():
    if "users" not in st.session_state:
        st.session_state.users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    init_users()
    if email in st.session_state.users:
        return False
    st.session_state.users[email] = hash_password(password)
    return True

def login_user(email, password):
    init_users()
    hashed = hash_password(password)
    return st.session_state.users.get(email) == hashed
