import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List
import warnings


def validate_database(db_path: Path, table_name: str):
    """Validate that database and table exists"""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    if not cur.fetchone():
        raise ValueError(f"Table '{table_name}' not found")
    cur.execute("PRAGMA table_info(items)")
    print(cur.fetchall())


def validate_data(df: pd.DataFrame):
    if df.empty:
        warnings.warn("Database is empty")
    negative_prices = (df["sellPrice"] < 0).sum()
    negative_prices += (df["buyPrice"] < 0).sum()
    if negative_prices > 0:
        warnings.warn(f"Found {negative_prices} negative prices")
    negative_volumes = (df["sellVolume"] < 0).sum()
    negative_volumes += (df["buyVolume"] < 0).sum()
    if negative_volumes > 0:
        warnings.warn(f"Found {negative_volumes} negative volumes")
    df.dropna(subset=["timestamp", "item_id"])


def load_data(db_path, table_name: str = "items", **kwargs) -> pd.DataFrame:
    db_path = Path(db_path)
    validate_database(db_path, table_name)
    timespan = (1773771691642, 1773774931625)
    required_cols = []
    conditions = []
    if "timespan" in kwargs.keys():
        timespan = kwargs["timespan"]
    if "required_cols" in kwargs.keys():
        required_cols = kwargs["required_cols"]
    if "conditions" in kwargs.keys():
        conditions = kwargs["conditions"]
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            f"""
            SELECT {', '.join("p." + col for col in required_cols)}, i.name AS name
            FROM prices p
            JOIN items i ON p.item_id = i.id
            WHERE timestamp <= {timespan[1]}
            AND timestamp  >= {timespan[0]}
            {" AND ".join(conditions)}
            ORDER BY timestamp ASC
            """,
            conn,
        )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    if required_cols:
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    # validate_data(df)
    return df


def load_buy_offers(
    db_path, table_names: List = ["sell_offers", "buy_offers"], **kwargs
) -> pd.DataFrame:
    print("doing orders")
    db_path = Path(db_path)
    for name in table_names:
        validate_database(db_path, name)
    timespan = (1773771691642, 1773774931625)
    required_cols = []
    conditions = []
    limit = 0
    if "timespan" in kwargs.keys():
        timespan = kwargs["timespan"]
    print("doing query")
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            f"""
            SELECT {"" if not kwargs["required_cols"] else ', '.join("b." + col for col in kwargs["required_cols"])}, i.name AS name
            FROM buy_offers b
            JOIN items i ON b.item_id = i.id
            WHERE timestamp <= {timespan[1]}
            AND timestamp  >= {timespan[0]}
            {"" if not kwargs["conditions"] else "AND " + " AND ".join(kwargs["conditions"])}
            ORDER BY timestamp ASC
            {"" if not kwargs["limit"] else f"LIMIT {kwargs["limit"]}"}
            """,
            conn,
        )
    print("query done")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    if False:
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    # validate_data(df)
    return df


def load_sell_offers(
    db_path, table_names: List = ["sell_offers", "buy_offers"], **kwargs
) -> pd.DataFrame:
    print("doing orders")
    db_path = Path(db_path)
    for name in table_names:
        validate_database(db_path, name)
    timespan = (1773771691642, 1773774931625)
    required_cols = []
    conditions = []
    limit = 0
    if "timespan" in kwargs.keys():
        timespan = kwargs["timespan"]
    print("doing query")
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            f"""
            SELECT {"" if not kwargs["required_cols"] else ', '.join("b." + col for col in kwargs["required_cols"])}, i.name AS name
            FROM sell_offers b
            JOIN items i ON b.item_id = i.id
            WHERE timestamp <= {timespan[1]}
            AND timestamp  >= {timespan[0]}
            {"" if not kwargs["conditions"] else "AND " + " AND ".join(kwargs["conditions"])}
            ORDER BY timestamp ASC
            {"" if not kwargs["limit"] else f"LIMIT {kwargs["limit"]}"}
            """,
            conn,
        )
    print("query done")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    if False:
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    # validate_data(df)
    return df


if __name__ == "__main__":
    df = load_data(
        "/home/oliver/rndm/bz/bazaar3.db",
        required_cols=[
            "timestamp",
            "sellPrice",
            "buyPrice",
            "sellVolume",
            "buyVolume",
        ],
        timespan=(1773771691642, 1773774931625),
    )
    print(df[df["name"] == "TARANTULA_WEB"])
    df = load_buy_offers(
        "/home/oliver/rndm/bz/bazaar3.db",
        required_cols=["timestamp", "price", "volume"],
        timespan=(1773771691642, 1773774931625),
        conditions=["name = 'TARANTULA_WEB'"],
        limit=10000,
    )
    print(df)
    df = load_sell_offers(
        "/home/oliver/rndm/bz/bazaar3.db",
        required_cols=["timestamp", "price", "volume"],
        timespan=(1773771691642, 1773774931625),
        conditions=["name = 'TARANTULA_WEB'"],
        limit=10000,
    )
    print(df)
