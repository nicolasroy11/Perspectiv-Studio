import pandas as pd
import numpy as np
import pytest

from llm_trader.intelligence.context_summarizer import (
    ContextSummarizer,
    TrendState,
    RsiZone,
    FeatureSet,
    ContextSummary,
)


def make_df(rsi=50.0, ema_fast=1.1, ema_slow=1.0, atr=0.001, candles=20):
    """Helper to generate minimal valid OHLCV frame."""
    return pd.DataFrame({
        "open": np.linspace(1.0, 1.2, candles),
        "high": np.linspace(1.05, 1.25, candles),
        "low": np.linspace(0.95, 1.15, candles),
        "close": np.linspace(1.0, 1.2, candles),
        "volume": np.linspace(1000, 2000, candles),
        "rsi": [rsi] * candles,
        "ema_fast": [ema_fast] * candles,
        "ema_slow": [ema_slow] * candles,
        "adx": [40] * candles,
        "atr": [atr] * candles,
    })


def test_summarizer_returns_context_summary():
    df = make_df()
    summary = ContextSummarizer().summarize(df)

    assert isinstance(summary, ContextSummary)
    assert isinstance(summary.features, FeatureSet)
    assert isinstance(summary.features.trend_state, TrendState)
    assert isinstance(summary.features.rsi_zone, RsiZone)
    assert isinstance(summary.features.volume, float)
    assert isinstance(summary.features.close, float)
    assert isinstance(summary.text, str)
    assert "Trend:" in summary.text


def test_rsi_zone_logic():
    s = ContextSummarizer()
    assert s._rsi_zone(20) == RsiZone.OVERSOLD
    assert s._rsi_zone(80) == RsiZone.OVERBOUGHT
    assert s._rsi_zone(50) == RsiZone.NEUTRAL
    assert s._rsi_zone(None) == RsiZone.UNKNOWN


def test_trend_state_logic():
    s = ContextSummarizer()
    assert s._trend_state(make_df(ema_fast=2, ema_slow=1), 2, 1) == TrendState.UP
    assert s._trend_state(make_df(ema_fast=1, ema_slow=2), 1, 2) == TrendState.DOWN
    assert s._trend_state(make_df(ema_fast=1, ema_slow=1), 1, 1) == TrendState.FLAT


def test_atr_rank_calculation():
    s = ContextSummarizer()
    df = make_df(atr=0.001)
    rank = s._atr_rank(df, 0.001)
    assert 0.0 <= rank <= 1.0


def test_empty_dataframe_raises():
    s = ContextSummarizer()
    with pytest.raises(ValueError):
        s.summarize(pd.DataFrame())
