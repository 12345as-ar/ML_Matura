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
        "SELECT name From sqlite_master WHERE type='table' AND name=?",
        table_name,
    )
    if not cur.fetchone():
        raise ValueError(f"Table '{table_name}' not found")


def validate_data(df: pd.DataFrame) -> bool:
    if df.empty:
        return False
    negative_prices = (df["price"] < 0).sum()
    if negative_prices > 0:
        warnings.warn(f"Found {negative_prices} negative prices")
    df.dropna(subset=["timestamp", "item_id"])
    return True


def get_data(db_path: Path, table_name: str):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            f"SELECT timestamp, price, timestamp, item_id FROM {table_name}", conn
        )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    required_cols = ["timestamp", "price", "item_id"]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")


def load_data(
    db_path,
    table_name: str = "items",
    item_ids: Optional[List[int]] = None,
) -> pd.DataFrame:
    db_path = Path(db_path)
    validate_database(db_path, table_name)
    return pd.DataFrame()
