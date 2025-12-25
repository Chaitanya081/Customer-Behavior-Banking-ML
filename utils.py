import pandas as pd
import streamlit as st
from sklearn.preprocessing import LabelEncoder

@st.cache_data
def load_data():
    return pd.read_csv("data/bank_marketing.csv", sep=";")

def encode(df):
    le = LabelEncoder()
    for col in df.select_dtypes(include="object"):
        df[col] = le.fit_transform(df[col])
    return df
