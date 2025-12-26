import streamlit as st

def apply_style():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #061a2e, #081f33);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
