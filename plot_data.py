import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

def plot_time_series(df: pd.DataFrame, variable: str, items: list):
    df = df.copy()
    df.index = pd.to_datetime(df.index, unit="ms")
    print("Original index range:")
    print(df.index.min(), df.index.max())
    print("Number of rows:", len(df))
    ax = None
    for item in items:
        dfi = df[df["name"] == item]
        if not ax:
            ax = dfi["sellPrice"].plot(label=item)
        else:
            dfi["price"].plot(ax=ax, label=item)
    ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%d.%m.%Y %H:%M")
    )
    plt.gcf().autofmt_xdate()
    ax.set_xlabel("timestamp")
    ax.set_ylabel("price")
    ax.set_title(variable + " over time")
    ax.legend()
    plt.show()

