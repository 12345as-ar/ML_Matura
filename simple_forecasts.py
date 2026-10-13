from re import X
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


def persistence(df: pd.DataFrame):
    split = int(len(df) * 0.8)

    test = df.iloc[split:]
    test["previous_sellPrice"] = test["sellPrice"].shift(1)
    test = test.dropna()

    X_test = test["previous_sellPrice"]
    y_test = test["sellPrice"]
    print(X_test, y_test)
    mse = mean_squared_error(y_test, X_test)
    return mse


def linear_regression(df: pd.DataFrame):
    split = int(len(df) * 0.8)

    train = df.iloc[:split]
    test = df.iloc[split:]
    test["previous_sellPrice"] = test["sellPrice"].shift(1)
    test = test.dropna()

    train["previous_sellPrice"] = train["sellPrice"].shift(1)
    train = train.dropna()

    X_train = train[["previous_sellPrice"]]
    y_train = train["sellPrice"]

    X_test = test[["previous_sellPrice"]]
    y_test = test["sellPrice"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    return mse
