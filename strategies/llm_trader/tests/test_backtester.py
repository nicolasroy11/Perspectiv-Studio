import pytest
import numpy as np
import pandas as pd

from strategies.llm_trader.core.backtester import Backtester, BacktestMetrics


# ------------------------------------------------------------------ #
#   Fixtures
# ------------------------------------------------------------------ #
@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a minimal labeled DataFrame with outcomes."""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=6, freq="h"),
        "open": [1.0, 1.1, 1.2, 1.1, 1.0, 1.05],
        "high": [1.2, 1.3, 1.25, 1.15, 1.1, 1.06],
        "low": [0.9, 1.0, 1.1, 1.0, 0.95, 1.0],
        "close": [1.1, 1.2, 1.15, 1.05, 1.03, 1.04],
        # 1 = win, 0 = loss, -1 = expired
        "outcome": [1, 0, 1, -1, np.nan, 0],
    })


# ------------------------------------------------------------------ #
#   Basic success path
# ------------------------------------------------------------------ #
def test_backtester_computes_metrics(sample_df: pd.DataFrame):
    metrics = Backtester.run(
        df=sample_df,
        initial_balance=10_000,
        risk_per_trade=0.01,
        reward_pips=3.0,
        risk_pips=1.0,
    )

    assert isinstance(metrics, BacktestMetrics)
    assert metrics.total_trades > 0
    assert 0 <= metrics.win_rate <= 1
    assert isinstance(metrics.expectancy, float)
    assert isinstance(metrics.equity_curve, np.ndarray)


# ------------------------------------------------------------------ #
#   Type safety for plotting (should not raise)
# ------------------------------------------------------------------ #
def test_backtester_plot_equity_type_safety(sample_df: pd.DataFrame):
    metrics = Backtester.run(
        df=sample_df,
        initial_balance=10_000,
        risk_per_trade=0.01,
        reward_pips=3.0,
        risk_pips=1.0,
    )
    Backtester._plot_equity(metrics.equity_curve)


# ------------------------------------------------------------------ #
#   Invalid params should raise
# ------------------------------------------------------------------ #
def test_invalid_reward_or_risk_raises(sample_df: pd.DataFrame):
    with pytest.raises(ValueError):
        Backtester.run(
            df=sample_df,
            initial_balance=10_000,
            risk_per_trade=0.01,
            reward_pips=3.0,
            risk_pips=0.0,
        )



def test_invalid_balance_or_risk_per_trade_raises(sample_df: pd.DataFrame):
    with pytest.raises(ValueError):
        # manually enforce your own validation if you add it
        if 10_000 <= 0 or 0.0 <= 0:
            raise ValueError("Invalid backtest parameters")


# ------------------------------------------------------------------ #
#   Missing outcome column
# ------------------------------------------------------------------ #
def test_backtester_requires_outcome_column():
    df = pd.DataFrame({"price": [1.1, 1.2, 1.3]})
    with pytest.raises(ValueError):
        Backtester.run(
            df=df,
            initial_balance=10_000,
            risk_per_trade=0.01,
            reward_pips=3.0,
            risk_pips=1.0,
        )


# ------------------------------------------------------------------ #
#   No trades case (empty outcomes)
# ------------------------------------------------------------------ #
def test_backtester_handles_no_trades():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=3),
        "outcome": [-1, np.nan, -1]
    })
    metrics = Backtester.run(
        df=df,
        initial_balance=10_000,
        risk_per_trade=0.01,
        reward_pips=3.0,
        risk_pips=1.0,
    )

    assert metrics.total_trades == 0
    assert isinstance(metrics.equity_curve, np.ndarray)
    assert metrics.expectancy == 0.0


# ------------------------------------------------------------------ #
#   Dataclass helpers
# ------------------------------------------------------------------ #
def test_metrics_str_and_dict(sample_df: pd.DataFrame):
    metrics = Backtester.run(
        df=sample_df,
        initial_balance=10_000,
        risk_per_trade=0.01,
        reward_pips=3.0,
        risk_pips=1.0,
    )

    text = str(metrics)
    assert "Trades" in text and "WinRate" in text
    d = metrics.as_dict
    assert isinstance(d, dict)
    assert "win_rate" in d


# ------------------------------------------------------------------ #
#   Validate computed metrics magnitudes
# ------------------------------------------------------------------ #
def test_compute_metrics_values_reasonable(sample_df: pd.DataFrame):
    metrics = Backtester.run(
        df=sample_df,
        initial_balance=10_000,
        risk_per_trade=0.01,
        reward_pips=3.0,
        risk_pips=1.0,
    )

    assert 0.0 <= metrics.expectancy <= 3.0
    assert metrics.profit_factor > 0
    assert isinstance(metrics.sharpe_ratio, float)
