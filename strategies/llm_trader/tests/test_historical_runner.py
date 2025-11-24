"""
Test suite for llm_trader.core.historical_runner
Ensures that HistoricalRunner executes, produces metrics,
and writes valid output files (Parquet + JSON).
"""

import pandas as pd
import numpy as np
from pathlib import Path
from strategies.llm_trader.runner.historical_runner import HistoricalRunner


def _make_mock_data(path: Path) -> None:
    """Create a small artificial OHLCV dataset for testing."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=48, freq="h"),
        "open": np.linspace(1.10, 1.20, 48),
        "high": np.linspace(1.11, 1.21, 48),
        "low": np.linspace(1.09, 1.19, 48),
        "close": np.linspace(1.10, 1.20, 48),
        "volume": 1000,
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)


def test_historical_runner_produces_output(tmp_path: Path):
    """Integration test: runner executes end-to-end and saves metrics files."""
    data_path = tmp_path / "eurusd_5m.parquet"
    _make_mock_data(data_path)

    runner = HistoricalRunner(
        data_path=data_path,
        output_dir=tmp_path,
        window_size_days=1,
        step_size_days=1,
        rsi_window=7,
        reward_pips=3,
        risk_pips=1,
        lookahead=3,
        pip_size=0.0001,
        initial_balance=10000,
        risk_per_trade=0.01,
    )

    result_df = runner.run()

    # --- structural checks ---
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    assert {"win_rate", "expectancy", "profit_factor"}.issubset(result_df.columns)

    # --- file outputs ---
    parquet_files = list(tmp_path.glob("*.parquet"))
    json_files = list(tmp_path.glob("*.json"))
    assert len(parquet_files) > 0, "Parquet output should exist"
    assert len(json_files) > 0, "JSON output should exist"


def test_historical_runner_handles_empty_data(tmp_path: Path):
    """Ensure runner gracefully handles no data (returns empty df)."""
    empty_path = tmp_path / "empty.parquet"
    pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"]).to_parquet(empty_path)

    runner = HistoricalRunner(
        data_path=empty_path,
        output_dir=tmp_path,
        window_size_days=1,
        step_size_days=1,
        rsi_window=7,
        reward_pips=3,
        risk_pips=1,
        lookahead=3,
        pip_size=0.0001,
        initial_balance=10000,
        risk_per_trade=0.01,
    )

    result_df = runner.run()
    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty
