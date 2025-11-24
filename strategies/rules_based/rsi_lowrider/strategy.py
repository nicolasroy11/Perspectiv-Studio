from __future__ import annotations
from dataclasses import dataclass
from typing import List
import pandas as pd
import pandas_ta as ta

from models.candle import Candle
from brokers.base import BaseBroker


@dataclass
class RSILowriderConfig:
    rsi_period: int = 7 * 2
    rsi_oversold_level: int = 30
    rung_size_in_pips: float = 2.0
    tp_target_in_pips: float = 2.0
    lot_size: float = 2.0


class RSILowriderStrategy:

    def __init__(self, config: RSILowriderConfig = RSILowriderConfig()):
        self.config = config
        self._candles: List[Candle] = []
        self._last_rsi: float = -1.0

    # -----------------------------------------------------
    # Utility: compute RSI (returns float, never None)
    # -----------------------------------------------------
    def _compute_rsi(self) -> float:
        if len(self._candles) < self.config.rsi_period + 1:
            return 0.0

        closes = [c.close for c in self._candles]
        rsi_series = ta.rsi(pd.Series(closes), length=self.config.rsi_period)
        val = rsi_series.iloc[-1]
        return float(val) if not pd.isna(val) else 0.0

    # -----------------------------------------------------
    # Utility: convert pips into price movement
    # -----------------------------------------------------
    def _pips(self, p: float) -> float:
        return p * 0.0001

    # -----------------------------------------------------
    # MAIN ENTRY — called every new candle
    # -----------------------------------------------------
    def on_candle(self, broker: BaseBroker, candle: Candle):
        self._candles.append(candle)

        # Compute current RSI
        rsi_now = self._compute_rsi()


        # ---- 2-CANDLE RSI-CURL RULE ----
        anchor_signal = False
        if self._last_rsi is not None:
            was_below = self._last_rsi <= self.config.rsi_oversold_level
            curled_up = rsi_now > self._last_rsi
            anchor_signal = (was_below and curled_up)

        position = broker.get_active_position()
        has_position = position is not None

        # ==========================================================
        # 1) ANCHOR ENTRY — ONLY if we do not already have a position
        # ==========================================================
        if anchor_signal and not has_position:

            anchor_price = candle.close
            tp_price = anchor_price + self._pips(self.config.tp_target_in_pips)

            # Market buy anchor
            broker.place_market_buy(
                lot_size=self.config.lot_size,
                tp_price=tp_price,
            )

            # First rung (pending limit buy)
            rung_entry = anchor_price - self._pips(self.config.rung_size_in_pips)
            rung_tp = rung_entry + self._pips(self.config.tp_target_in_pips)

            broker.add_rung(
                entry_price=rung_entry,
                tp_price=rung_tp,
                lot_size=self.config.lot_size,
                ladder_position=1,
            )

        # ==========================================================
        # 2) LADDER LOGIC — only when we already have a position
        # ==========================================================
        elif has_position:
            self._process_rungs(broker, candle)

        # Update last RSI
        self._last_rsi = rsi_now

    # ------------------------------------------------------------------
    # Add next rung only after deepest rung is fully active (not pending)
    # ------------------------------------------------------------------
    def _process_rungs(self, broker: BaseBroker, candle: Candle):

        position = broker.get_active_position()
        if not position:
            return

        trades = position.trades

        # deepest rung index
        deepest = max(t.ladder_position for t in trades)

        # get the deepest rung trade
        last_rung_trade = next(t for t in trades if t.ladder_position == deepest)

        # only add new rung if deepest rung is FILLED (not pending)
        if last_rung_trade.is_pending:
            return

        new_level = deepest + 1
        new_entry = last_rung_trade.entry_price - self._pips(self.config.rung_size_in_pips)
        new_tp = new_entry + self._pips(self.config.tp_target_in_pips)

        broker.add_rung(
            entry_price=new_entry,
            tp_price=new_tp,
            lot_size=self.config.lot_size,
            ladder_position=new_level,
        )
