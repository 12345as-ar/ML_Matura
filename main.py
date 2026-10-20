import data_loader
import prepare_data
import simple_forecasts
import plot_data
item = "SUMMONING_EYE"
df = data_loader.load_data(
    "/home/oliver/rndm/bz/bazaar3.db",
    required_cols=[
        "timestamp",
        "sellPrice",
        "item_id",
    ],
    conditions=[f"name = '{item}'"]
)
DC = prepare_data.DataCleaner()

df = DC.clean_price_time_series(df)
#df["sellPrice"] = df["sellPrice"].pct_change()
plot_data.plot_time_series(df, "price",[item])
df = df[df["name"] == item]
print("persistence mse: ", simple_forecasts.persistence(df))
print("linear_regression mse: ", simple_forecasts.linear_regression(df))
