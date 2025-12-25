import streamlit as st

def apply_style():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #061a2e, #081f33);
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b2a45, #061a2e);
    }

    div[data-testid="metric-container"] {
        background-color: #0f3456;
        border: 1px solid #1c4e80;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.5);
    }

    h1, h2, h3 {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
