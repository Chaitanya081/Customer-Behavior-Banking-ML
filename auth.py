import streamlit as st
import hashlib

# simple in-memory user store
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    if "users" not in st.session_state:
        st.session_state.users = {}

    if email in st.session_state.users:
        return False

    st.session_state.users[email] = hash_password(password)
    return True

def login_user(email, password):
    if "users" not in st.session_state:
        return False

    return st.session_state.users.get(email) == hash_password(password)
