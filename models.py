from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def segment_customers(df):
    features = df[["age", "balance", "campaign", "duration"]]

    kmeans = KMeans(n_clusters=3, random_state=42)
    df["segment"] = kmeans.fit_predict(features)

    return df

def predict_risk(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X)[:, 1]

    risk_labels = []
    for p in probs:
        if p > 0.7:
            risk_labels.append("High")
        elif p > 0.4:
            risk_labels.append("Medium")
        else:
            risk_labels.append("Low")

    return risk_labels
