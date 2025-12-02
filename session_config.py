# Session variables
from dataclasses import dataclass
from data.constants.forex_instruments import ForexInstruments


INSTRUMENT = ForexInstruments.EURUSD
CANDLES_RESOLUTION = "1m"
FETCH_COUNT = 70           # how many candles we grab each run
INTERVAL_MINUTES = 1        # run every N minutes on the minute
MAX_ALLOWABLE_SIMULTANEOUS_POSITIONS = 3
MAX_SPREAD_PIPS = 0.4

@dataclass(frozen=True)
class RSI_LOWRIDER_CONFIG:
    RSI_PERIOD: int = 7
    RSI_OVERSOLD_LEVEL: int = 30
    RUNG_SIZE_IN_PIPS: float = 1.3
    TP_TARGET_IN_PIPS: float = 1.0
    LOT_SIZE: float = 0.01