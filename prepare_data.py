import sqlite3
import pandas as pd
import numpy


def check_complete(db: str) -> dict[int, int]:
    print("beginning")
    con = sqlite3.connect(db)
    cur = con.cursor()
    hours = {}
    current_time = 0
    cur.execute("SELECT timestamp FROM prices WHERE item_id IS 1")
    timestamps = cur.fetchall()
    last_time = int(timestamps[0][0] / 1000)
    segments = 0
    total = 0
    print("gonna loop")
    for index, timestamp in enumerate(timestamps, start=1):
        time = int(timestamp[0] / 1000)
        print(time)
        gap = time - last_time
        if 0 <= gap <= 120:
            current_time += gap
        else:
            segments += 1
            total += current_time
            total_hours = round(current_time / 3600)
            if total_hours in hours.keys():
                hours[total_hours] += 1
            else:
                hours[total_hours] = 1
        last_time = time
    print(total / segments)
    return hours


def item_id_to_name(item_id: int) -> str:
    return "TARANTULA_WEB"


class DataCleaner:
    def __init__(
        self,
        gap_threshold_minutes: int = 5,
        time_jumps_minutes: int = 1,
        interpolation: str = "linear",
        outlier_method: str = "keep",
        outlier_threshold: float = 2.0,
        start_time: int = 1773771691642,
        end_time: int = 1773774931625,
        required_cols: list = [
            "timestamp",
            "sellPrice",
            "buyPrice",
            "sellVolume",
            "buyVolume",
        ],
    ):
        self.gap_threshold_minutes = gap_threshold_minutes
        self.time_jumps_minutes = time_jumps_minutes
        self.interpolation = interpolation
        self.outlier_method = outlier_method
        self.outlier_threshold = outlier_threshold
        self.cleaning_report = {}
        self.start_time = start_time
        self.end_time = end_time
        self.required_cols = required_cols
        pass

    def clean_price_time_series(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = self._remove_duplicates(df)
        df_clean = df_clean.dropna()
        df_clean = self._fill_missing_rows(df_clean)
        df_clean = self._interpolate_prices(df_clean)
        return df_clean

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(df)
        df_clean = df.drop_duplicates(
            subset=["timestamp", "item_id"], keep="first"
        )
        self.cleaning_report["duplicates removed"] = initial_count - len(
            df_clean
        )
        return df_clean

    def _fill_missing_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        for i in range(2000):
            if (df["item_id"] == i).any():
                new_rows = []
                current_df = df[df["item_id"] == i]
                example_row = current_df.iloc[0].to_dict()
                current_df = current_df.sort_values("timestamp")["timestamp"]
                time = self.start_time
                for rec_time in current_df:
                    while rec_time - time > 120000:
                        for col in self.required_cols:
                            new_row = {}
                            if col == "timestamp":
                                new_row["timestamp"] = time
                            elif col in [
                                "price",
                                "buyVolume",
                                "sellVolume",
                                "volume",
                            ]:
                                new_row[col] = numpy.nan
                            else:
                                new_row[col] = example_row[col]
                        time += 60000
                    time = rec_time
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        return df

    def _interpolate_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        # fill missing timestamps

        if self.interpolation == "linear":
            df_clean = df.sort_values("timestamp")
            for column in df.columns:
                if column in ["price", "buyVolume", "sellVolume", "volume"]:
                    df_clean[column] = df_clean.groupby("item_id")[
                        column
                    ].transform(
                        lambda x: x.interpolate(
                            method="linear", limit_direction="both"
                        )
                    )
            return df_clean
        return df


if __name__ == "__main__":
    print("hello")
    
   # sorted_result = dict(
   #     sorted(
   #         check_complete(
       #         "../skyblock/bazaar_collector_py/bazaar.db"
       #     ).items(),
       #     key=lambda item: item[1],
       #     reverse=True,
    #    )
  #  )
    import data_loader
    df = data_loader.load_data(
        "/home/oliver/rndm/bz/bazaar3.db",
        required_cols=[
            "timestamp",
            "sellPrice",
            "buyPrice",
            "sellVolume",
            "buyVolume",
            "item_id",
        ],
        timespan=(1773771691642, 1773774931625),
    )
    DC = DataCleaner()
    df = DC.clean_price_time_series(df)
    print(df[df["name"] == "TARANTULA_WEB"])
