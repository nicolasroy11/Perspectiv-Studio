import pandas as pd
import numpy as np
from llm_trader.core import indicator_engine

def make_mock_df(n=100):
    idx = pd.date_range("2024-01-01", periods=n, freq="5min")
    return pd.DataFrame({
        "timestamp": idx,
        "open": np.linspace(1.1, 1.2, n),
        "high": np.linspace(1.11, 1.21, n),
        "low": np.linspace(1.09, 1.19, n),
        "close": np.linspace(1.1, 1.2, n) + np.random.normal(0, 0.0005, n),
        "volume": np.random.randint(100, 500, n)
    })

def test_add_rsi_columns():
    df = indicator_engine.add_rsi(make_mock_df(), window=7)
    assert "rsi" in df.columns
    assert not df["rsi"].isna().all()

def test_add_all_indicators_shape():
    df = indicator_engine.add_indicators(make_mock_df(200), 7, 10, 140, 14, 14)
    expected_cols = {"rsi", "ema_fast", "ema_slow", "adx", "atr"}
    assert expected_cols.issubset(df.columns)
    assert len(df) > 0

