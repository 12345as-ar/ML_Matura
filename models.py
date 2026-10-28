import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

def random_forest_regression(df:pd.DataFrame):
    split = int(len(df) * 0.8)

    train = df.iloc[:split].copy()
    test = df.iloc[split:].copy()
    prices = []
    for i in range(1, previous_prices + 1):
        test["previous_sellPrice"+str(i)] = test["sellPrice"].shift(i)
        train["previous_sellPrice"+str(i)] = train["sellPrice"].shift(i)
        prices.append("previous_sellPrice"+str(i))
    test = test.dropna()

    train = train.dropna()

    X_train = train[prices]
    y_train = train["sellPrice"]

    X_test = test[prices]
    y_test = test["sellPrice"]

