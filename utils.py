import pandas as pd

def load_data():
    return pd.read_csv("data/bank_marketing.csv", sep=";")
