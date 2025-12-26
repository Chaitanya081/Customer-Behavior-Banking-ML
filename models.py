import pandas as pd
import numpy as np

def customer_metrics():
    return {
        "total_customers": 45211,
        "high_risk": 12,
        "retention": 88
    }


def bar_chart_data():
    return pd.DataFrame({
        "Category": ["Low Risk", "Medium Risk", "High Risk", "Very High"],
        "Customers": [20, 35, 15, 30]
    })


def predict_customer(age, balance, campaign):
    score = age * 0.02 + balance * 0.00001 - campaign * 0.5
    if score > 3:
        return "High Risk"
    elif score > 1.5:
        return "Medium Risk"
    return "Low Risk"
