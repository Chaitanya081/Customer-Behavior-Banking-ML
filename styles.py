import streamlit as st

def load_styles():
    st.markdown("""
        <style>
        body { background-color: #0e1117; }
        h1, h2, h3 { color: #00c6ff; }
        </style>
    """, unsafe_allow_html=True)
