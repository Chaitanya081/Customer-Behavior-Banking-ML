from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def segment_customers(df):
    features = df[["age", "balance", "campaign", "duration"]]
    model = KMeans(n_clusters=3, random_state=42)
    df["segment"] = model.fit_predict(features)
    return df

def predict_risk(df):
    X = df.drop("y", axis=1)
    y = df["y"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    df["risk_score"] = model.predict_proba(X)[:,1]

    df["risk"] = df["risk_score"].apply(
        lambda x: "High" if x > 0.7 else "Medium" if x > 0.4 else "Low"
    )

    return df
