import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


def persistence(df: pd.DataFrame):
    split = int(len(df) * 0.8)

    test = df.iloc[split:]
    df["previous_price"] = df["price"].shift(1)
    df.dropna()

    X_test = test["previous_price"]
    y_test = test["price"]

    mse = mean_squared_error(y_test, X_test)
    return mse


def linear_regression(df: pd.DataFrame):
    split = int(len(df) * 0.8)

    train = df.iloc[:split]
    test = df.iloc[split:]
    df["previous_price"] = df["price"].shift(1)
    df.dropna()

    X_train = train[["previous_price"]]
    y_train = train["price"]

    X_test = test[["previous_price"]]
    y_test = test["price"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    return mse


def random_forest(df: pd.DataFrame):
    pass

def gradient_boosting(df: pd.DataFrame):
    pass

def arima(df: pd.DataFrame):
    pass

def lstm(df: pd.DataFrame):
    pass

def transformer(df: pd.DataFrame):
    pass
