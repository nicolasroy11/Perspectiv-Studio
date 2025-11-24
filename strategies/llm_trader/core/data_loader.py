"""
data_loader.py
---------------
Loads OHLCV data from CSV/Parquet and validates schema.
"""

import pandas as pd


REQUIRED_COLS = ["timestamp", "open", "high", "low", "close", "volume"]


import pandas as pd
from pathlib import Path


def load_ohlcv(path: str | Path) -> pd.DataFrame:
    """
    Load OHLCV data from CSV or Parquet file automatically.

    Args:
        path: Path to .csv or .parquet file.

    Returns:
        DataFrame with standard OHLCV columns.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    # Optional standardization for downstream use
    required_cols = {"open", "high", "low", "close"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required OHLC columns in {path.name}")

    return df

