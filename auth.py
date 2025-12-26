import streamlit as st

def init_auth():
    if "users" not in st.session_state:
        st.session_state.users = {}
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def register_user(email, password):
    init_auth()
    if email in st.session_state.users:
        return False
    st.session_state.users[email] = password
    return True


def login_user(email, password):
    init_auth()
    if email in st.session_state.users and st.session_state.users[email] == password:
        st.session_state.logged_in = True
        st.session_state.current_user = email
        return True
    return False


def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None
