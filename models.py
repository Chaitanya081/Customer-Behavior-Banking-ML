from sklearn.cluster import KMeans

def segment_customers(df):
    features = df[["age", "balance", "campaign", "duration"]]
    kmeans = KMeans(n_clusters=3, random_state=42)
    df["segment"] = kmeans.fit_predict(features)
    return df

def predict_risk_single(age, balance, duration, campaign):
    score = 0
    if age < 30: score += 1
    if balance < 0: score += 2
    if duration < 100: score += 2
    if campaign > 3: score += 1

    if score >= 4:
        return "High Risk"
    elif score >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"
