# brokers/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Iterable, Tuple

from models.candle import Candle
from models.cycle import Cycle
from models.account_snapshot import AccountSnapshot
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

    @abstractmethod
    def refresh(self):
        """Handles necessary cycling of broker API parameters, ie. they changed their API payload keys."""
        pass

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
    
    @abstractmethod
    def get_candles_range(
        self,
        symbol: str,
        resolution: str,
        date_from: datetime,
        date_to: datetime,
    ) -> List[Candle]:
        pass
    
    @abstractmethod
    def get_current_bid_ask(self) -> Tuple[float, float]:
        """Return (bid, ask) for the instrument."""
        pass
    
    @abstractmethod
    def get_current_spread(self) -> float:
        """Returns spread:float for the instrument."""
        pass

    # ----------------------------------------------------------------------
    # Simple trade primitives
    # ----------------------------------------------------------------------

    @abstractmethod
    def place_limit_buy(
        self,
        entry_price: float,
        lot_size: float,
        tp_price: float | None = None,
        strategy_id: str | None = None,
    ) -> str:
        """
        Place a LIMIT BUY order.
        If tp_price is supplied, attach a take-profit immediately.
        """
        pass

    @abstractmethod
    def close_trade(self, trade: Trade, exit_price: float | None = None) -> Trade:
        """Close an individual trade."""
        pass
    
    @abstractmethod
    async def close_all(self) -> bool:
        """Close all open positions at market price and cancel all pending trades"""
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
        strategy_id: str
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
    # Cycle / account view
    # ----------------------------------------------------------------------
    
    @abstractmethod
    def get_account_snapshot(self, date_from: datetime, date_to: datetime) -> AccountSnapshot:
        pass
    
    @abstractmethod
    def get_open_trades(self) -> List[Trade]:
        pass

    @abstractmethod
    def get_active_cycle(self) -> Cycle | None:
        pass

    @abstractmethod
    def flatten_all(self) -> Iterable[Trade]:
        """Close all active trades for this instrument."""
        pass
