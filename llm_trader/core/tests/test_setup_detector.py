import pandas as pd
import numpy as np
from llm_trader.core import setup_detector

def test_detect_rsi_reversal_breakout_flags_correct():
    df = pd.DataFrame({
        "high": [1.100, 1.101, 1.102, 1.105],
        "low": [1.099, 1.098, 1.099, 1.102],
        "close": [1.099, 1.098, 1.100, 1.106],
        "rsi": [25, 28, 35, 40],
    })
    df = setup_detector.detect_rsi_reversal_breakout(df, lookback=3)
    assert bool(df["setup"].iloc[-1])
    assert df["setup"].sum() >= 1  # at least one valid setup


def test_detect_rsi_reversal_breakout_no_trigger_when_flat():
    df = pd.DataFrame({
        "high": [1.100, 1.101, 1.102, 1.103],
        "low": [1.099, 1.099, 1.099, 1.099],
        "close": [1.100, 1.101, 1.102, 1.103],
        "rsi": [50, 52, 54, 55],
    })
    df = setup_detector.detect_rsi_reversal_breakout(df)
    assert not df["setup"].any()
