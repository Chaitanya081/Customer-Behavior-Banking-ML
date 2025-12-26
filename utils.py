import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def load_data():
    return pd.read_csv("data/bank_marketing.csv", sep=";")

def prepare_ml_data(df):
    df = df.copy()

    # Target encoding
    df["y"] = df["y"].map({"yes": 1, "no": 0})

    categorical_cols = df.select_dtypes(include="object").columns
    numeric_cols = df.select_dtypes(exclude="object").columns.drop("y")

    encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
    encoded_cat = encoder.fit_transform(df[categorical_cols])

    encoded_cat_df = pd.DataFrame(
        encoded_cat,
        columns=encoder.get_feature_names_out(categorical_cols)
    )

    final_df = pd.concat(
        [df[numeric_cols].reset_index(drop=True), encoded_cat_df],
        axis=1
    )

    return final_df, df["y"]
