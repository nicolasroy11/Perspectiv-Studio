from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(slots=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @staticmethod
    def empty():
        c = Candle(
            timestamp = datetime.now(timezone.utc),
            open = 0.0,
            high = 0.0,
            low = 0.0,
            close = 0.0,
            volume = 0.0
        )
        return c