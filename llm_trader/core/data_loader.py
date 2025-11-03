"""
data_loader.py
---------------
Loads OHLCV data from CSV/Parquet and validates schema.
"""

import pandas as pd


REQUIRED_COLS = ["timestamp", "open", "high", "low", "close", "volume"]


def load_ohlcv(path: str) -> pd.DataFrame:
    """
    Load and validate OHLCV data

    Args:
        path: Path to csv file

    Returns:
        Cleaned DataFrame indexed by timestamp (UTC)
    """
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df
