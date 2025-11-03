"""
Ensures every setup detector in llm_trader.core.setup_detector
returns a DataFrame containing a 'setup' column.
"""

import inspect
import pandas as pd
import pytest
from llm_trader.core import setup_detector

# --- Sample minimal data shared by all detectors ---
@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "open": [1.1000, 1.1010, 1.1020],
        "high": [1.1010, 1.1020, 1.1030],
        "low":  [1.0990, 1.1005, 1.1015],
        "close":[1.1005, 1.1015, 1.1025],
        "rsi":  [35.0, 29.0, 28.5],
    })


def get_detector_functions():
    """Dynamically collect all detector functions in setup_detector module."""
    for name, obj in inspect.getmembers(setup_detector, inspect.isfunction):
        if name.startswith("detect_"):
            yield name, obj


@pytest.mark.parametrize("func_name,func", list(get_detector_functions()))
def test_detector_returns_setup_column(func_name, func, sample_df):
    """Every detector must return a DataFrame with a 'setup' column."""
    df_out = func(sample_df.copy())
    assert isinstance(df_out, pd.DataFrame), f"{func_name} did not return a DataFrame"
    assert "setup" in df_out.columns, f"{func_name} missing 'setup' column"
    assert df_out["setup"].dtype == bool, f"{func_name} 'setup' must be boolean"
