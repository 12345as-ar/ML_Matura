import pandas
import numpy as np
from scipy.signal import periodogram
from scipy.stats import entropy
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.feature_selection import mutual_info_regression
from statsmodels.sandbox.stats.runs import runstest_1samp


def check_autocorrelation(df: pandas.DataFrame):
    prices = df["sellPrice"].to_numpy()
    returns = np.diff(np.log(prices))
    res = [
        float(pandas.Series(returns).autocorr(lag=i))
        for i in (1, 5, 15, 60, 1440, 10080)
    ]
    return res


def hurst_exponent(df: pandas.DataFrame):
    prices = df["sellPrice"].to_numpy()

    with np.errstate(divide="ignore"):
        series = np.diff(np.log(prices))
    x = np.asarray(series, dtype=float)
    x = x[np.isfinite(x)]

    if len(x) < 100:
        return np.nan

    sizes = np.unique(
        np.logspace(np.log10(10), np.log10(len(x) // 4), num=15).astype(int)
    )

    rs_values = []

    for size in sizes:
        n_chunks = len(x) // size
        chunks = x[: n_chunks * size].reshape(n_chunks, size)

        chunk_rs = []

        for chunk in chunks:
            std = np.std(chunk, ddof=1)

            if std == 0:
                continue

            deviations = np.cumsum(chunk - np.mean(chunk))
            R = np.max(deviations) - np.min(deviations)

            chunk_rs.append(R / std)

        if chunk_rs:
            rs_values.append((size, np.mean(chunk_rs)))

    if len(rs_values) < 5:
        return np.nan

    sizes_used, rs = np.array(rs_values).T

    H, _ = np.polyfit(np.log(sizes_used), np.log(rs), 1)

    return float(H)


def spectral_entropy_returns(df: pandas.DataFrame):
    prices = df["sellPrice"].to_numpy()

    with np.errstate(divide="ignore"):
        returns = np.diff(np.log(prices))

    x = np.asarray(returns, dtype=float)
    x = x[np.isfinite(x)]

    if len(x) < 10:
        return np.nan

    x = x - np.mean(x)
    if np.allclose(x, 0):
        return 0.0

    frequencies, power = periodogram(x)

    power = power[1:]

    if len(power) == 0 or power.sum() == 0:
        return np.nan

    probabilities = power / power.sum()

    return float(entropy(probabilities) / np.log(len(probabilities)))


def ljung_box_p_value(df: pandas.DataFrame):
    prices = df["sellPrice"].to_numpy()

    with np.errstate(divide="ignore"):
        returns = np.diff(np.log(prices))
    result = acorr_ljungbox(
        returns, lags=[1, 5, 15, 60, 1440, 10080], return_df=True
    )
    values = result["lb_stat"].tolist() + result["lb_pvalue"].tolist()
    for v in values:
        v = float(v)
    return values


def outlier_rate(df: pandas.DataFrame):
    prices = df["sellPrice"].to_numpy()

    with np.errstate(divide="ignore"):
        returns = np.diff(np.log(prices))
    median = np.median(returns)
    mad = np.median(np.abs(returns - median))

    if mad > 0:
        threshold = 6 * 1.4826 * mad
        outliers = np.abs(returns - median) > threshold
        outlier_rate = np.mean(outliers)
    else:
        outlier_rate = 0.0

    return float(outlier_rate)


def volatility(df: pandas.DataFrame):
    prices = df["sellPrice"].to_numpy()

    with np.errstate(divide="ignore"):
        returns = np.diff(np.log(prices))
    return float(returns.std())


def mutual_information(returns: pandas.DataFrame):
    result = []
    for lag in [1,5,15,60,1440,10080]:
        data = pandas.DataFrame(
            {"past_return": returns["sellPrice"].shift(lag), "future_return": returns["sellPrice"]}
        ).dropna()

        X = data[["past_return"]]
        y = data["future_return"]

        result.append(float(mutual_info_regression(X, y, random_state=42)[0]))
    return result


def variance_ratio(returns, ):
    result = []
    for q in [2,5,15,60,1440,10080]:
        single_var = returns["sellPrice"].var(ddof=1)
        if single_var == 0:
            result.append(np.nan)
            continue

        aggregated_returns = returns["sellPrice"].rolling(q).sum().dropna()
        result.append(aggregated_returns.var(ddof=1) / (q * single_var))
    print(result)
    return result


def volatility_stability(returns: pandas.DataFrame):
    rolling_vol_h = returns["sellPrice"].rolling(60).std().dropna()
    rolling_vol_d = returns["sellPrice"].rolling(1440).std().dropna()
    rolling_vol_w = returns["sellPrice"].rolling(10080).std().dropna()
    mean_vol_h = rolling_vol_h.mean()
    mean_vol_d = rolling_vol_d.mean()
    mean_vol_w = rolling_vol_w.mean()
    res_h = 0
    res_d = 0
    res_w = 0
    if mean_vol_h:
        res_h = rolling_vol_h.std() / mean_vol_h
    if mean_vol_d:
        res_d = rolling_vol_d.std() / mean_vol_d
    if mean_vol_w:
        res_w = rolling_vol_w.std() / mean_vol_w
    return [res_h, res_d, res_w]


def runs_test(returns):
    z_stat, p_value = runstest_1samp(returns["sellPrice"], cutoff=0)
    return [z_stat, p_value]


if __name__ == "__main__":
    import simple_forecasts
    import data_loader
    import prepare_data
    import sqlite3

    con = sqlite3.connect("data_folder/featuredb.db")
    cur = con.cursor()
    conn2 = sqlite3.connect(
        "/home/oliver/projects/skyblock/bazaar_collector_py/bazaar.db"
    )

    cur2 = conn2.cursor()
    cur2.execute("SELECT name FROM items")
    it = 1

    for item in cur2.fetchall()[1252:]:

        print("loaded Data ", item, f" {it}/2201")
        it = it + 1
        item = item[0]

        df = data_loader.load_data(
            "/home/oliver/rndm/bz/bazaar3.db",
            required_cols=[
                "timestamp",
                "sellVolume",
                "sellPrice",
                "item_id",
            ],
            conditions=[f"name = '{item}'"],
        )

        print(df.index.min(), df.index.max())
        DC = prepare_data.DataCleaner()
        df = DC.clean_price_time_series(df)
        values = [item]
        df = df[df["name"] == item]
        df["sellPrice"] = df["sellPrice"].replace(
            0, 0.1
        )  # valid because prices are only small not zero as long as there is activity
        returns = df.copy()
        returns["sellPrice"] = np.log(
            df["sellPrice"] / df["sellPrice"].shift(1)
        )
        returns = returns.dropna(subset=["sellPrice"])

        values.extend(check_autocorrelation(df))
        values.extend(ljung_box_p_value(df))
        values.append(hurst_exponent(df))
        values.append(spectral_entropy_returns(df))
        values.append(outlier_rate(df))
        values.append(volatility(df))
        values.append(simple_forecasts.persistence(df))
        values.append(simple_forecasts.linear_regression(df))
        values.append(simple_forecasts.persistence(returns))
        values.append(simple_forecasts.linear_regression(returns))
        values.append(df["sellVolume"].median())
        values.extend(runs_test(returns))
        values.extend(volatility_stability(returns))
        values.extend(variance_ratio(returns))
        values.extend(mutual_information(returns))
        print(len(values))

        cur.execute(
            """
            INSERT INTO data (
                    name, 
                    autocorr1, 
                    autocorr5, 
                    autocorr15,
                    autocorr60, 
                    autocorrday, 
                    autocorrweek, 
                    Ljungbox1, 
                    Ljungbox5, 
                    Ljungbox15, 
                    Ljungbox60, 
                    Ljungbox1440, 
                    Ljungbox10080, 
                    Ljungbox1p, 
                    Ljungbox5p, 
                    Ljungbox15p, 
                    Ljungbox60p, 
                    Ljungbox1440p, 
                    Ljungbox10080p, 
                    Hurst, 
                    Spectral, 
                    outlier_rate, 
                    volatility, 
                    persistancemse, 
                    linear_regressionmse, 
                    persistancereturnsmse, 
                    linear_regressionreturnsmse,
                    median_volume,
                    runs_test_z,
                    runs_test_p,
                    volatility_stability_h,
                    volatility_stability_d,
                    volatility_stability_w,
                    variance_ratio2,
                    variance_ratio5,
                    variance_ratio15,
                    variance_ratio60,
                    variance_ratio1440,
                    variance_ratio10080,
                    mutual_information1,
                    mutual_information5,
                    mutual_information15,
                    mutual_information60,
                    mutual_information1440,
                    mutual_information10080
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
            tuple(values),
        )

        con.commit()
