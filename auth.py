import streamlit as st
import hashlib

if "users" not in st.session_state:
    st.session_state.users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    if email in st.session_state.users:
        return False
    st.session_state.users[email] = hash_password(password)
    return True

def login_user(email, password):
    if email not in st.session_state.users:
        return False
    return st.session_state.users[email] == hash_password(password)
