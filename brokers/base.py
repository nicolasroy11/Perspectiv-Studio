# brokers/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Iterable

from models.candle import Candle
from models.position import Position
from models.trade import Trade
from models.forex_instrument import ForexInstrument


class BaseBroker(ABC):
    """
    Environment-agnostic broker interface (live / backtest / forward-test).

    Concrete implementations:
      - TradeLockerBroker (real)
      - BacktestBroker (simulation)
    """

    def __init__(self, instrument: ForexInstrument):
        self.instrument = instrument

    # ----------------------------------------------------------------------
    # Market data
    # ----------------------------------------------------------------------
    @abstractmethod
    def get_candles_range_from_csv(
        self,
        resolution: str,
        start: datetime,
        end: datetime,
    ) -> List[Candle]:
        pass

    # ----------------------------------------------------------------------
    # Simple trade primitives
    # ----------------------------------------------------------------------
    @abstractmethod
    def place_market_buy(
        self,
        lot_size: float,
        tp_price: float | None = None,
    ) -> Trade:
        """
        Place a market BUY order.
        If tp_price is supplied, attach a take-profit immediately.
        """
        pass

    @abstractmethod
    def place_limit_buy(
        self,
        entry_price: float,
        lot_size: float,
        tp_price: float | None = None,
    ) -> Trade:
        """
        Place a LIMIT BUY order.
        If tp_price is supplied, attach a take-profit immediately.
        """
        pass

    @abstractmethod
    def close_trade(self, trade: Trade, exit_price: float | None = None) -> Trade:
        """Close an individual trade."""
        pass

    # ----------------------------------------------------------------------
    # Unified rung creation (limit buy + TP)
    # ----------------------------------------------------------------------
    @abstractmethod
    def add_rung(
        self,
        entry_price: float,
        tp_price: float,
        lot_size: float,
        ladder_position: int,
    ) -> Trade:
        """
        Atomic: create a pending LIMIT BUY with a take-profit attached.

        This mirrors TradeLocker:
        - a limit buy
        - with a pre-specified limit TP
        - ladder_position is recorded for analysis only
        """
        pass

    # ----------------------------------------------------------------------
    # Position / account view
    # ----------------------------------------------------------------------
    @abstractmethod
    def get_open_trades(self) -> List[Trade]:
        pass

    @abstractmethod
    def get_active_position(self) -> Position | None:
        pass

    @abstractmethod
    def flatten_all(self) -> Iterable[Trade]:
        """Close all active trades for this instrument."""
        pass
