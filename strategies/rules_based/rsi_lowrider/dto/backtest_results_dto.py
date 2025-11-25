# rules_based/strategies/rsi_lowrider/dto/backtest_result_dto.py

from dataclasses import dataclass
from typing import List


@dataclass
class LowriderCandleState:
    """
    Full snapshot of strategy + broker state at a single candle.
    Intended for backtesting, forward-testing, visualization, and auditing.
    The prefix 'current_' refers to the value observed in the candle that just closed.
    The prefix 'previous_' refers to the value observed in the candle that closed before the one the just closed.
    """

    # --- Time & OHLCV ---
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    # --- Indicators ---
    current_rsi_value: float

    # --- Strategy events ---
    events: List[str]   # e.g. ["ANCHOR", "RUNG_FILLED", "TP_HIT"]

    # --- Ladder state ---
    num_active_rungs: int
    num_pending_rungs: int

    # --- Broker state ---
    num_active_trades: int
    num_pending_trades: int
    num_closed_trades: int

    # --- PnL & Equity ---
    realized_pnl: float
    unrealized_pnl: float
    equity: float


@dataclass
class LowriderBacktestResultsDto:
    series: List[LowriderCandleState]
