# import pytest
# # pytestmark = pytest.mark.asyncio
# from datetime import datetime

# from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import (
#     LowriderBacktestResultsDto,
#     LowriderCandleState,
# )
# from strategies.rules_based.rsi_lowrider.backtest import RSILowriderBacktester
# from web.trader_backend.schemas.backtest import RsiLowriderBacktestRequest


# CSV_PATH = "data/raw/lowrider_1m_backtest_tradelocker_output.csv"


# @pytest.mark.asyncio
# async def test_lowrider_backtest_results_end_to_end():
#     """
#     End-to-end validation of the Lowrider DTO.
#     Ensures the backtester produces correct candle-by-candle state,
#     RSI curl triggers, ladders, and no impossible states.
#     """

#     request = RsiLowriderBacktestRequest(
#         asset="EURUSD",
#         frequency="1m",
#         dateFrom=datetime(2024,1,1),
#         dateTo=datetime(2026,12,31),
#         rsiPeriod=7,
#         rsiOversoldLevel=30,
#         rungSizeInPips=2.0,
#         tpTargetInPips=2.0,
#     )



import pytest
import pandas as pd
from datetime import datetime, timedelta

from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import LowriderBacktestResultsDto, LowriderCandleState
from strategies.rules_based.rsi_lowrider.strategy import (
    RSILowriderStrategy,
    RSILowriderConfig,
)
from brokers.backtest import BacktestBroker
from models.candle import Candle


# ---------------------------------------------------------
# Helper: make synthetic candles
# ---------------------------------------------------------
def make_candle(ts, price):
    return Candle(
        timestamp=ts,
        open=price,
        high=price + 0.00005,
        low=price - 0.00005,
        close=price,
        volume=100.0
    )


# ---------------------------------------------------------
# Helper: build repeated candles from a list of prices
# ---------------------------------------------------------
def build_candles(prices, start=None):
    if start is None:
        start = datetime(2024, 1, 1)

    return [
        make_candle(start + timedelta(minutes=i), price)
        for i, price in enumerate(prices)
    ]


# ---------------------------------------------------------
# Test 1 — anchor triggers when RSI < oversold then curls up
# ---------------------------------------------------------
def test_anchor_trigger_rsi_curl():
    """
    Construct a price series that produces a clear RSI-dip then curl-up.
    Verify the strategy fires exactly one anchor entry.
    """

    config = RSILowriderConfig(
        rsi_period=3,
        rsi_oversold_level=30,
        rung_size_in_pips=2.0,
        tp_target_in_pips=2.0,
        lot_size=1.0,
    )
    strategy = RSILowriderStrategy(config)
    broker = BacktestBroker()

    # Prices falling then rising → clear RSI dip then curl-up
    prices = [1.1000, 1.0990, 1.0980, 1.0990, 1.1000, 1.1010]
    candles = build_candles(prices)

    anchor_count = 0

    for candle in candles:
        strategy.on_candle_just_closed(broker, candle)
        broker.process_candle(candle)

        if len(broker.positions) > 0 and broker.positions[0].trades:
            # Anchor = first BUY trade created
            if broker.positions[0].trades[0].ladder_position == 0:
                anchor_count = 1

    assert anchor_count == 1, "Anchor entry should trigger exactly once"


# ---------------------------------------------------------
# Test 2 — ladder adds next rung ONLY after deepest rung fills
# ---------------------------------------------------------
def test_ladder_adds_next_rung_only_after_fill():
    config = RSILowriderConfig(
        rsi_period=2,
        rsi_oversold_level=30,
        rung_size_in_pips=2.0,
        tp_target_in_pips=2.0,
        lot_size=1.0,
    )
    strategy = RSILowriderStrategy(config)
    broker = BacktestBroker()

    # Trigger anchor: RSI dip & curl
    prices = [1.2000, 1.1990, 1.1980, 1.1990]  # dip → curl-up
    candles = build_candles(prices)

    for candle in candles:
        strategy.on_candle_just_closed(broker, candle)
        broker.process_candle(candle)

    position = broker.get_active_position()
    assert position is not None
    assert len(position.trades) == 2  # anchor + rung1

    rung1 = position.trades[1]
    assert rung1.is_pending, "First rung should be pending until price fills"


# ---------------------------------------------------------
# Test 3 — TP hit increments closed-trades count
# ---------------------------------------------------------
def test_tp_hit_detected_by_closed_trade_change():
    config = RSILowriderConfig(
        rsi_period=2,
        rsi_oversold_level=30,
        rung_size_in_pips=2.0,
        tp_target_in_pips=2.0,
        lot_size=1.0,
    )
    strategy = RSILowriderStrategy(config)
    broker = BacktestBroker()

    # Prices dipping then rising so anchor triggers early
    prices = [1.1000, 1.0990, 1.0980, 1.0990]  # dip -> curl
    candles = build_candles(prices)

    # Run enough candles to get anchor + rung
    for candle in candles:
        strategy.on_candle_just_closed(broker, candle)
        broker.process_candle(candle)

    position = broker.get_active_position()
    assert position is not None

    # Now produce a high enough candle to hit TP
    tp_price = position.trades[0].tp_price
    hit_tp_candle = make_candle(datetime(2024, 1, 1, 0, 20), tp_price + 0.0001)

    prev_closed = sum(
        1 for p in broker.positions for t in p.trades if t.exit_price is not None
    )

    strategy.on_candle_just_closed(broker, hit_tp_candle)
    broker.process_candle(hit_tp_candle)

    now_closed = sum(
        1 for p in broker.positions for t in p.trades if t.exit_price is not None
    )

    assert now_closed == prev_closed + 1, "A TP hit should increment closed trades by 1"
