import pandas as pd

def risk_prediction(df):
    # Simple rule-based demo (safe & fast)
    df["risk"] = df["balance"].apply(
        lambda x: "High Risk" if x < 0 else "Low Risk"
    )
    return df
