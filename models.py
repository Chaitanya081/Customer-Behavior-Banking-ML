import pandas as pd

def simple_risk_prediction(age, balance, duration):
    score = 0
    if age < 25:
        score += 1
    if balance < 0:
        score += 2
    if duration < 100:
        score += 1

    if score >= 3:
        return "High Risk"
    elif score == 2:
        return "Medium Risk"
    else:
        return "Low Risk"
