# rules_based/strategies/rsi_lowrider/dto/backtest_result_dto.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LowriderCandleState:
    """
    Full snapshot of strategy + broker state at a single candle.
    Intended for backtesting, forward-testing, visualization, and auditing.
    """

    # --- Time & OHLCV ---
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    # --- Indicators ---
    rsi: float
    rsi_was_below_buy: bool
    rsi_curl: bool

    # --- Strategy events ---
    anchor_triggered: bool
    rung_added: Optional[int]                # ladder_position if created this candle
    events: List[str]                        # e.g. ["ANCHOR", "RUNG_FILLED", "TP_HIT"]

    # --- Ladder state ---
    deepest_rung: int
    active_rungs: int
    pending_rungs: int

    # --- Broker state ---
    num_active_trades: int
    num_pending_trades: int
    num_closed_trades: int
    entry_prices: List[float]
    tp_prices: List[float]

    # --- PnL & Equity ---
    realized_pnl: float
    unrealized_pnl: float
    equity: float


@dataclass
class LowriderBacktestResultsDto:
    series: List[LowriderCandleState]
