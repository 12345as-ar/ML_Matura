import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def plot_time_series(df: pd.DataFrame, variable: str, items: list):
    ax = None
    for item in items:
        dfi = df[df["name"] == item]
        if not ax:
            ax = dfi["price"].plot(label=item)
        else:
            dfi["price"].plot(ax=ax, label=item)
    ax.set_xlabel("timestamp")
    ax.set_ylabel("price")
    ax.set_title(variable + " over time")
    ax.legend()
    plt.show()


