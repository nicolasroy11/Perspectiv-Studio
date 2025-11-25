from dataclasses import dataclass


@dataclass(frozen=True)
class ForexInstrument:
    symbol: str
    pip_size: float            # minimum price movement (pip definition)
    dollars_per_pip_per_lot: float  # pip value for 1 standard lot
    description: str = ""
