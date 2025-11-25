from __future__ import annotations
from dataclasses import dataclass
from typing import List
import pandas as pd
import pandas_ta as ta

from models.candle import Candle
from brokers.base import BaseBroker


@dataclass
class RSILowriderConfig:
    rsi_period: int = 14
    rsi_oversold_level: int = 30
    rung_size_in_pips: float = 2.0
    tp_target_in_pips: float = 2.0
    lot_size: float = 2.0


class RSILowriderStrategy:

    def __init__(self, config: RSILowriderConfig = RSILowriderConfig()):
        self.config = config
        self.candles: List[Candle] = []
        self.rsi_list: List[float] = []

    # -----------------------------------------------------
    # Compute RSI for current candle
    # -----------------------------------------------------
    def compute_rsi(self) -> float:
        if len(self.candles) < self.config.rsi_period + 1:
            return 0.0

        closes = [c.close for c in self.candles]
        rsi_series = ta.rsi(pd.Series(closes), length=self.config.rsi_period)
        val = rsi_series.iloc[-1]

        return float(val) if not pd.isna(val) else 0.0

    # -----------------------------------------------------
    # Convert pips → price delta
    # -----------------------------------------------------
    def pips(self, p: float) -> float:
        return p * 0.0001

    # -----------------------------------------------------
    # MAIN ENTRY (renamed as requested)
    # -----------------------------------------------------
    def on_candle_just_closed(self, broker: BaseBroker, candle: Candle):
        self.candles.append(candle)

        # 1) Compute RSI for this candle
        current_rsi = self.compute_rsi()

        # 2) Push into history
        self.rsi_list.append(current_rsi)

        # 3) Determine anchor signal from last two RSI values
        enter_position = False
        if len(self.rsi_list) >= 2:
            previous_rsi = self.rsi_list[-2]
            current_rsi = self.rsi_list[-1]

            was_below = previous_rsi <= self.config.rsi_oversold_level
            curled_up = current_rsi > previous_rsi

            enter_position = (was_below and curled_up)

        # 4) Determine if position exists
        position = broker.get_active_position()
        has_position = position is not None

        # ==================================================
        # 1) ANCHOR ENTRY
        # ==================================================
        if enter_position and not has_position:

            anchor_price = candle.close
            tp_price = anchor_price + self.pips(self.config.tp_target_in_pips)

            # Market buy
            broker.place_market_buy(
                lot_size=self.config.lot_size,
                tp_price=tp_price,
            )

            # First rung
            rung_entry = anchor_price - self.pips(self.config.rung_size_in_pips)
            rung_tp = rung_entry + self.pips(self.config.tp_target_in_pips)

            broker.add_rung(
                entry_price=rung_entry,
                tp_price=rung_tp,
                lot_size=self.config.lot_size,
                ladder_position=1,
            )

        # ==================================================
        # 2) LADDER LOGIC
        # ==================================================
        elif has_position:
            self.process_rungs(broker, candle)

    # -----------------------------------------------------
    # Ladder logic unchanged
    # -----------------------------------------------------
    def process_rungs(self, broker: BaseBroker, candle: Candle):

        position = broker.get_active_position()
        if not position:
            return

        trades = position.trades
        deepest = max(t.ladder_position for t in trades)

        last_rung_trade = next(t for t in trades if t.ladder_position == deepest)

        if last_rung_trade.is_pending:
            return

        new_level = deepest + 1
        new_entry = last_rung_trade.entry_price - self.pips(self.config.rung_size_in_pips)
        new_tp = new_entry + self.pips(self.config.tp_target_in_pips)

        broker.add_rung(
            entry_price=new_entry,
            tp_price=new_tp,
            lot_size=self.config.lot_size,
            ladder_position=new_level,
        )
