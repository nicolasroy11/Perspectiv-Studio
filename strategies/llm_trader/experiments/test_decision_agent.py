# llm_trader/tests/test_decision_agent.py
from __future__ import annotations

import json
import pytest
import pandas as pd
from typing import Any, Union

from strategies.llm_trader.intelligence.context_summarizer import (
    ContextSummarizer,
    ContextSummary,
)
from strategies.llm_trader.intelligence.decision_agent import (
    DecisionAgent,
    Decision,
    DecisionResult,
    MockLLM,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Minimal synthetic OHLCV dataset for summarization tests."""
    # Explicitly allow DatetimeIndex in union
    data: dict[str, Union[pd.DatetimeIndex, list[float | int]]] = {
        "timestamp": pd.date_range("2025-01-01", periods=10, freq="5min"),
        "open":  [1.1000, 1.1010, 1.1020, 1.1030, 1.1040, 1.1050, 1.1060, 1.1070, 1.1080, 1.1090],
        "high":  [1.1010, 1.1020, 1.1030, 1.1040, 1.1050, 1.1060, 1.1070, 1.1080, 1.1090, 1.1100],
        "low":   [1.0990, 1.1000, 1.1010, 1.1020, 1.1030, 1.1040, 1.1050, 1.1060, 1.1070, 1.1080],
        "close": [1.1010, 1.1020, 1.1030, 1.1040, 1.1050, 1.1060, 1.1070, 1.1080, 1.1090, 1.1100],
        "volume": [100.0] * 10,
        "rsi": [25.0, 28.0, 31.0, 32.0, 34.0, 36.0, 38.0, 42.0, 47.0, 52.0],
        "ema_fast": [1.101, 1.102, 1.103, 1.104, 1.105, 1.106, 1.107, 1.108, 1.109, 1.110],
        "ema_slow": [1.100, 1.101, 1.102, 1.103, 1.104, 1.105, 1.106, 1.107, 1.108, 1.109],
        "adx": [20.0] * 10,
        "atr": [0.0003] * 10,
    }
    return pd.DataFrame(data)


@pytest.fixture
def summarizer() -> ContextSummarizer:
    """Fixture providing a configured summarizer."""
    return ContextSummarizer(n_candles=10)


@pytest.fixture
def mock_agent() -> DecisionAgent:
    """Fixture providing a deterministic DecisionAgent using MockLLM."""
    return DecisionAgent(llm_client=MockLLM())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_agent_produces_valid_decision(
    sample_df: pd.DataFrame,
    summarizer: ContextSummarizer,
    mock_agent: DecisionAgent,
) -> None:
    """Agent returns a valid DecisionResult with typed fields."""
    context: ContextSummary = summarizer.summarize(sample_df)
    result: DecisionResult = mock_agent.evaluate(
        context=context,
        setup_name="RSI<30_breakout",
        rr_ratio=1.6,
        lookahead_bars=20,
    )

    assert isinstance(result, DecisionResult)
    assert isinstance(result.action, Decision)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.rationale, str)
    assert result.action in {Decision.ENTER, Decision.SKIP, Decision.REVERSE}


def test_agent_returns_expected_json_keys(
    sample_df: pd.DataFrame,
    summarizer: ContextSummarizer,
    mock_agent: DecisionAgent,
) -> None:
    """DecisionResult serializes to dict cleanly and includes required keys."""
    context: ContextSummary = summarizer.summarize(sample_df)
    result: DecisionResult = mock_agent.evaluate(context, "RSI<30_breakout", 1.6, 20)
    result_dict: dict[str, Any] = result.as_dict()

    assert set(result_dict.keys()) == {"action", "confidence", "rationale"}
    assert isinstance(result_dict["action"], str)
    assert isinstance(result_dict["confidence"], float)
    assert isinstance(result_dict["rationale"], str)


def test_mock_llm_deterministic_behavior(
    sample_df: pd.DataFrame,
    summarizer: ContextSummarizer,
) -> None:
    """MockLLM should yield identical decisions for identical prompts."""
    context: ContextSummary = summarizer.summarize(sample_df)
    agent: DecisionAgent = DecisionAgent(llm_client=MockLLM())

    result_1: DecisionResult = agent.evaluate(context, "RSI<30_breakout", 1.6, 20)
    result_2: DecisionResult = agent.evaluate(context, "RSI<30_breakout", 1.6, 20)

    assert result_1.as_dict() == result_2.as_dict()
    assert result_1.confidence == pytest.approx(result_2.confidence, rel=1e-9)


def test_parsing_handles_non_json_gracefully(
    sample_df: pd.DataFrame,
    summarizer: ContextSummarizer,
) -> None:
    """Agent must handle malformed LLM responses gracefully."""
    class BrokenLLM:
        def __call__(self, prompt: str) -> str:
            return "nonsense output not json"

    agent: DecisionAgent = DecisionAgent(llm_client=BrokenLLM())
    context: ContextSummary = summarizer.summarize(sample_df)
    result: DecisionResult = agent.evaluate(context, "RSI<30_breakout", 1.6, 20)

    assert result.action == Decision.SKIP
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.rationale, str)


def test_confidence_is_clamped(
    sample_df: pd.DataFrame,
    summarizer: ContextSummarizer,
) -> None:
    """Confidence above 1.0 or below 0.0 should be clamped into range."""
    class OverconfidentLLM:
        def __call__(self, prompt: str) -> str:
            return json.dumps({
                "action": "ENTER",
                "confidence": 3.14,
                "reason": "overconfident"
            })

    agent: DecisionAgent = DecisionAgent(llm_client=OverconfidentLLM())
    context: ContextSummary = summarizer.summarize(sample_df)
    result: DecisionResult = agent.evaluate(context, "RSI<30_breakout", 1.6, 20)

    assert result.confidence == 1.0


def test_action_defaults_to_skip(
    sample_df: pd.DataFrame,
    summarizer: ContextSummarizer,
) -> None:
    """Missing or invalid 'action' field should default to SKIP."""
    class NoActionLLM:
        def __call__(self, prompt: str) -> str:
            return json.dumps({
                "confidence": 0.4,
                "reason": "missing action field"
            })

    agent: DecisionAgent = DecisionAgent(llm_client=NoActionLLM())
    context: ContextSummary = summarizer.summarize(sample_df)
    result: DecisionResult = agent.evaluate(context, "RSI<30_breakout", 1.6, 20)

    assert result.action == Decision.SKIP
    assert result.confidence == pytest.approx(0.4)
    assert "missing" in result.rationale.lower()
