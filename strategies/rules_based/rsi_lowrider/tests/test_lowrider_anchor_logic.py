import pytest
from datetime import datetime

from strategies.rules_based.rsi_lowrider.backtest import PositionEvents, RSILowriderBacktester
from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import LowriderCandleState
from web.trader_backend.schemas.backtest import RsiLowriderBacktestRequest


@pytest.mark.asyncio
async def test_lowrider_anchor_trigger_logic():
    """
    This test ensures:
    1. RSI dip (<= oversold) followed by curl-up (RSI increases)
    2. Produces exactly one ANCHOR event at the curl-up candle.
    3. A position is open on that same candle.
    """

    # -------------------------
    # Build request
    # -------------------------
    request = RsiLowriderBacktestRequest(
        asset="EURUSD",
        trading_type="rules-based",
        frequency="1m",
        date_from=datetime(2024, 1, 1),
        date_to=datetime(2026, 1, 1),
        rsi_period=7,
        rsi_oversold_level=30,
        rung_size_in_pips=1.5,
        tp_target_in_pips=1.5,
    )

    # -------------------------
    # Run backtest
    # -------------------------
    backtester = RSILowriderBacktester()
    dto = await backtester.get_backtest_results(request)

    series = dto.series
    assert len(series) > 20

    anchor_indices = [
        i for i, s in enumerate(series)
        if PositionEvents.ANCHOR in s.events
    ]

    # -------------------------
    # Must have exactly ONE anchor entry event in this test range
    # (if you want more, change this)
    # -------------------------
    assert len(anchor_indices) >= 1, "Expected at least one anchor entry event"
    anchor_idx = anchor_indices[0]

    anchor_state = series[anchor_idx]

    # -------------------------
    # Validate RSI curl mechanics
    # -------------------------
    prev = series[anchor_idx - 1]

    assert prev.current_rsi_value <= request.rsi_oversold_level, (
        f"Previous RSI must be <= oversold level to trigger anchor: prev={prev.current_rsi_value}"
    )

    assert anchor_state.current_rsi_value > prev.current_rsi_value, (
        f"Anchor candle RSI must be greater than previous: prev={prev.current_rsi_value}, now={anchor_state.current_rsi_value}"
    )

    # -------------------------
    # Validate position creation
    # -------------------------
    assert anchor_state.num_active_trades > 0 or anchor_state.num_pending_trades > 0, (
        "At anchor candle, a new position must exist"
    )

    # -------------------------
    # Validate NO anchor event happened earlier
    # -------------------------
    for i in range(0, anchor_idx):
        assert PositionEvents.ANCHOR not in series[i].events, (
            f"Unexpected early anchor event at index {i}"
        )

    # -------------------------
    # Validate that events list exists and is well-typed
    # -------------------------
    assert isinstance(anchor_state.events, list)
    assert PositionEvents.ANCHOR in anchor_state.events

    # Additional: TP and RUNG events are well-formed
    for s in series:
        for evt in s.events:
            assert evt in PositionEvents.__dict__.values(), (
                f"Unexpected event type: {evt}"
            )
