import data_loader
import prepare_data
import simple_forecasts

df = data_loader.load_data(
    "/home/oliver/rndm/bz/bazaar3.db",
    required_cols=[
        "timestamp",
        "sellPrice",
        "item_id",
    ],
    conditions=["name = 'BOOSTER_COOKIE'"]
)
DC = prepare_data.DataCleaner()

df = DC.clean_price_time_series(df)

df = df[df["name"] == "BOOSTER_COOKIE"]
print("persistence mse: ", simple_forecasts.persistence(df))
print("linear_regression mse: ", simple_forecasts.linear_regression(df))
