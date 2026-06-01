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
    negative_prices = (df["price"] < 0).sum()
    if negative_prices > 0:
        warnings.warn(f"Found {negative_prices} negative prices")
    df.dropna(subset=["timestamp", "item_id"])


def get_data(db_path: Path, table_name: str) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT p.*, i.name AS table_name
            FROM prices p
            JOIN items i ON p.item_id = i.id
            """,
            conn,
        )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    required_cols = [
        "item_id",
        "timestamp",
        "sellPrice",
        "buyPrice",
        "sellVolume",
        "buyVolume",
        "sellOrders",
        "buyOrders",
    ]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    validate_data(df)
    return df


def load_data(
    db_path,
    table_name: str = "items",
) -> pd.DataFrame:
    db_path = Path(db_path)
    validate_database(db_path, table_name)
    return get_data(db_path, table_name)


if __name__ == "__main__":
    df = load_data("/home/oliver/rndm/bz/bazaar3.db")
    print((df["string"]))
