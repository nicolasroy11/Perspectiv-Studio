from typing import List
import pandas as pd
import pandas_ta as ta

from models.candle import Candle
import session_config as config

rsi_lowrider_config = config.RSI_LOWRIDER_CONFIG

class RSILowriderSignals:

    def __init__(self):
        self.candles: List[Candle] = []
        self.rsi_list: List[float] = []

    # -----------------------------------------------------
    # Compute RSI for current candle
    # -----------------------------------------------------
    def compute_rsi(self, candles: List[Candle]) -> float:
        closes = [c.close for c in candles]
        rsi_series = ta.rsi(pd.Series(closes), length=rsi_lowrider_config.RSI_PERIOD)
        val = rsi_series.iloc[-1]

        return float(val) if not pd.isna(val) else 0.0
    
    def should_enter_long_position(self, candles: List[Candle]) -> bool:
        # 1) Compute RSI for this candle
        current_rsi = self.compute_rsi(candles)

        # 2) Push into history
        self.rsi_list.append(current_rsi)
        
        enter_position = False
        if len(self.rsi_list) >= 2:
            previous_rsi = self.rsi_list[-2]
            current_rsi = self.rsi_list[-1]

            was_below = previous_rsi <= rsi_lowrider_config.RSI_OVERSOLD_LEVEL
            was_very_low = 1 < current_rsi < 20
            curled_up = current_rsi > previous_rsi

            enter_position = ((was_below and curled_up) or was_very_low)
        
        return enter_position
    