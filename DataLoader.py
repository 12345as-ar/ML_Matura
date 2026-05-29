import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List
import warnings


class DataLoader:
    def __init__(self, db_path: str, table_name: str = "items"):
        self.db_path = Path(db_path)
        self.table_name = table_name
        conn = sqlite3.connect(self.db_path)
        self.cur = conn.cursor()
        self.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (self.table_name,),
        )
        if not self.cur.fetchone():
            raise ValueError(f"Table '{self.table_name}' not found")


def validate_database(db_path: Path):
    """Validate that database and table exists"""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")


def load_data(
    db_path,
    table_name: str = "items",
    item_ids: Optional[List[int]] = None,
) -> pd.DataFrame:
    db_path = Path(db_path)
    validate_database(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT name From sqlite_master WHERE type='table' AND name=?",
        table_name,
    )
    if not cur.fetchone():
        raise ValueError(f"Table '{table_name}' not found")

