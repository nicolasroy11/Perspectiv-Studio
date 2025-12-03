# brokers/backtest_broker.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Iterable

import pandas as pd

from brokers.base import BaseBroker
from brokers.tradelocker import TradeLockerBroker
from models.trade import Trade, Side
from models.cycle import Cycle
from models.candle import Candle
import runtime_settings as rs


PIP = 0.0001
LADDER_PIPS = 2     # 2-pip spacing down the ladder
TP_PIPS = 2         # 2-pip take-profit above entry
COMMISSION = rs.ROUNDTRIP_COMMISSION_PER_LOT


class BacktestBroker(BaseBroker):
    """
    A deterministic broker simulation for 1-minute candle backtesting.
    - One and only one active Position at a time.
    - A Position is a list of Trades.
    - A Trade is pending until filled.
    - A Trade is filled if candle.low <= price <= candle.high.
    - TP is executed if candle.high >= tp_price.
    - Only one TP fill per candle (like real TL behavior).
    """

    def __init__(self, symbol: str = "EURUSD", csv_path: Optional[str] = "data/raw/lowrider_1m_backtest_tradelocker_output.csv"):
        # NOTE: we intentionally do NOT call BaseBroker.__init__ here,
        # to avoid forcing a ForexInstrument dependency right now.
        self.symbol = symbol

        # If provided, this CSV is used by get_candles_range().
        # Expected columns: timestamp,open,high,low,close,volume
        self.csv_path = csv_path

        self.positions: List[Cycle] = []  # all positions ever created, open or closed
        self.current_position: Optional[Cycle] = None

        # These are set as candles are processed
        self._current_timestamp: Optional[datetime] = None
        self._last_close: Optional[float] = None

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------

    def _generate_trade_id(self) -> str:
        return f"t{len(self.positions)}_{datetime.now(tz=timezone.utc).timestamp()}"

    def position_is_open(self) -> bool:
        return (
            self.current_position is not None and
            not self.current_position.is_closed
        )

    def open_new_position(self) -> Cycle:
        """Called automatically when placing the anchor."""
        pos = Cycle(symbol=self.symbol, positions=[])
        self.positions.append(pos)
        self.current_position = pos
        return pos

    # ----------------------------------------------------------------------
    # BaseBroker: market data
    # ----------------------------------------------------------------------
    def get_candles_range_from_csv(
        self,
        file_path: str,
        resolution: str,
        date_from: datetime,
        date_to: datetime,
    ) -> List[Candle]:
        """
        Load candles from the configured CSV and return the slice between
        start and end (inclusive).

        CSV format:
            timestamp,open,high,low,close,volume
        timestamp example:
            2025-02-25 21:45:00+00:00
        """
        if file_path is None:
            raise RuntimeError(
                "BacktestBroker.csv_path is not set. "
                "Set broker.csv_path to a CSV file before calling get_candles_range()."
            )

        df = pd.read_csv(file_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        # Normalize start/end to UTC-aware for robust comparison
        if date_from.tzinfo is None:
            date_from = date_from.replace(tzinfo=df["timestamp"].dt.tz)
        if date_to.tzinfo is None:
            date_to = date_to.replace(tzinfo=df["timestamp"].dt.tz)

        mask = (df["timestamp"] >= date_from) & (df["timestamp"] <= date_to)
        sliced = df.loc[mask].sort_values("timestamp")

        candles: List[Candle] = []
        for _, row in sliced.iterrows():
            candles.append(
                Candle(
                    timestamp=row["timestamp"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
            )

        return candles
    
    def get_candles_range_from_tradelocker(
        self,
        symbol: str,
        resolution: str,
        date_from: datetime,
        date_to: datetime
    ) -> List[Candle]:
        """
        Load candles from TradeLocker by default
        """

        broker = TradeLockerBroker()
        candles = broker.get_candles_range(symbol=symbol, resolution=resolution, date_from=date_from, date_to=date_to)

        return candles

    # ----------------------------------------------------------------------
    # Original "core broker" methods (kept, used internally)
    # ----------------------------------------------------------------------

    def place_market_order(
        self,
        symbol: str,
        side: Side,
        lot_size: float,
        tp_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        ladder_position: int = 0,
    ) -> Trade:

        if symbol != self.symbol:
            raise ValueError("BacktestBroker only supports one symbol at a time.")

        if self._last_close is None or self._current_timestamp is None:
            raise RuntimeError(
                "BacktestBroker._last_close or _current_timestamp is not set. "
                "Make sure you drive the broker with process_candle() first."
            )

        entry_price = self._last_close  # set by strategy driving the broker
        now = self._current_timestamp

        trade = Trade(
            id=self._generate_trade_id(),
            cycle_id=None,         # set later
            symbol=symbol,
            side=side,
            lot_size=lot_size,
            executed_price=entry_price,
            open_time=now,
            tp_price=tp_price,
            sl_price=sl_price,
            ladder_position=ladder_position,
            is_pending=False,
            raw={},
        )

        pos = self.open_new_position()

        trade.cycle_id = id(pos)
        pos.positions.append(trade)

        return trade

    def place_limit_order(
        self,
        symbol: str,
        side: Side,
        lot_size: float,
        limit_price: float,
        tp_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        ladder_position: int = 0,
    ) -> Trade:

        now = self._current_timestamp or datetime.now(tz=timezone.utc)

        trade = Trade(
            id=self._generate_trade_id(),
            cycle_id=None,
            symbol=symbol,
            side=side,
            lot_size=lot_size,
            executed_price=limit_price,
            open_time=now,
            tp_price=tp_price,
            sl_price=sl_price,
            ladder_position=ladder_position,
            is_pending=True,
            raw={},
        )

        if not self.current_position:
            position = self.open_new_position()
        else:
            position = self.current_position

        trade.cycle_id = id(position)
        position.positions.append(trade)

        return trade

    def get_open_positions(self) -> Optional[Cycle]:
        """Returns the single current position (if open)."""
        if self.position_is_open():
            return self.current_position
        return None

    def get_all_positions(self) -> List[Cycle]:
        return self.positions

    # ----------------------------------------------------------------------
    # Candle simulation entry point
    # ----------------------------------------------------------------------

    def process_candle(self, candle: Candle):
        """
        Called once per candle by the backtest loop.

        Handles:
        - Filling pending limit buys
        - Executing one TP max per candle
        - Updating broker timestamps / close price
        """

        self._current_timestamp = candle.timestamp
        self._last_close = candle.close

        if not self.current_position:
            return

        position = self.current_position

        # 1) Fill pending limit buys if candle trades through limit price
        for trade in position.positions:
            if trade.is_pending and candle.low <= trade.executed_price <= candle.high:
                trade.is_pending = False
                trade.open_time = candle.timestamp

        # 2) Take profits — ONLY ONE TP PER CANDLE
        #    Pick the highest TP available that can be hit
        filled_tps = [
            trade for trade in position.positions
            if (not trade.is_pending) and trade.exit_price is None and trade.tp_price is not None
        ]

        if filled_tps:
            candidates = [t for t in filled_tps if candle.high >= t.tp_price]
            if candidates:
                trade_to_close = max(candidates, key=lambda t: t.tp_price)
                trade_to_close.exit_price = trade_to_close.tp_price
                trade_to_close.close_time = candle.timestamp

        # If all trades closed, position ends
        if position.is_closed:
            self.current_position = None

    # ----------------------------------------------------------------------
    # BaseBroker: simple trade primitives (BUY-only for Lowrider)
    # ----------------------------------------------------------------------

    def place_market_buy(
        self,
        lot_size: float,
        tp_price: float | None = None,
    ) -> Trade:
        """
        Thin wrapper around place_market_order for a BUY on self.symbol.
        """
        return self.place_market_order(
            symbol=self.symbol,
            side="buy",
            lot_size=lot_size,
            tp_price=tp_price,
            sl_price=None,
            ladder_position=0,
        )

    def place_limit_buy(
        self,
        entry_price: float,
        lot_size: float,
        tp_price: float | None = None,
    ) -> Trade:
        """
        Thin wrapper around place_limit_order for a BUY on self.symbol.
        """
        return self.place_limit_order(
            symbol=self.symbol,
            side="buy",
            lot_size=lot_size,
            limit_price=entry_price,
            tp_price=tp_price,
            sl_price=None,
            ladder_position=0,
        )

    def close_trade(self, trade: Trade, exit_price: float | None = None) -> Trade:
        """
        Close an individual trade at the given price (or last close).
        Does NOT currently compute realized_pnl; you can layer that on later.
        """
        if exit_price is None:
            if self._last_close is None:
                raise RuntimeError("BacktestBroker._last_close is not set.")
            exit_price = self._last_close

        now = self._current_timestamp or datetime.utcnow()

        trade.exit_price = exit_price
        trade.close_time = now
        trade.is_pending = False

        return trade

    # ----------------------------------------------------------------------
    # BaseBroker: unified rung creation (limit + TP)
    # ----------------------------------------------------------------------

    def add_rung(
        self,
        entry_price: float,
        tp_price: float,
        lot_size: float,
        ladder_position: int,
    ) -> Trade:
        """
        Atomic: create a pending LIMIT BUY with a take-profit attached.
        (For backtest, this just delegates to place_limit_order.)
        """
        return self.place_limit_order(
            symbol=self.symbol,
            side="buy",
            lot_size=lot_size,
            limit_price=entry_price,
            tp_price=tp_price,
            sl_price=None,
            ladder_position=ladder_position,
        )

    # ----------------------------------------------------------------------
    # BaseBroker: position / account view
    # ----------------------------------------------------------------------

    def get_open_trades(self) -> List[Trade]:
        """
        All trades in the active position that are not yet closed
        (includes both pending and filled-but-open).
        """
        if not self.current_position:
            return []

        position = self.current_position
        return [t for t in position.positions if t.exit_price is None]

    def get_active_cycle(self) -> Cycle | None:
        """
        Single active position (if any).
        """
        return self.current_position if self.position_is_open() else None

    def flatten_all(self) -> Iterable[Trade]:
        """
        Close all active trades for this symbol at the last known close.
        """
        flattened: List[Trade] = []

        if not self.current_position:
            return flattened

        position = self.current_position

        for trade in position.positions:
            if trade.exit_price is None:
                flattened.append(self.close_trade(trade))

        # If everything is now closed, clear current_position
        if position.is_closed:
            self.current_position = None

        return flattened

    # -------------------------------------------------------------
    # PnL helpers for the backtester
    # -------------------------------------------------------------
    def realized_pnl(self) -> float:
        """
        Sum of realized PnL from all closed trades across all positions.
        """
        total = 0.0
        for pos in self.positions:
            for t in pos.positions:
                if t.exit_price is not None:
                    # If the trade model already has realized_pnl, use it.
                    if t.realized_pnl is not None:
                        total += t.realized_pnl
                    else:
                        # fallback computation
                        total += (t.exit_price - t.executed_price) * t.lot_size * 10000
        return total

    def unrealized_pnl(self, current_price: float) -> float:
        """
        Sum of unrealized PnL for the *active* position only.
        """
        pos = self.get_active_cycle()
        if pos is None:
            return 0.0

        total = 0.0
        for t in pos.positions:
            if t.exit_price is None:  # open trade
                total += (current_price - t.executed_price) * t.lot_size * 10000

        return total
