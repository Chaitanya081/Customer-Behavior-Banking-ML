import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression

def preprocess(df):
    df = df.copy()
    for col in df.select_dtypes(include="object"):
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
    return df

def predict_risk(df):
    df = preprocess(df)

    X = df.drop("y", axis=1)
    y = df["y"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    return model.predict(X[:1])[0]
