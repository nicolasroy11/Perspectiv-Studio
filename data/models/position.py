from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Position:
    entry_price: float
    tp_price: Optional[float]
    lot_size: float
    direction: str
    opened_at: datetime = datetime.now(timezone.utc)

    # These remain None until the position is closed
    exit_price: Optional[float] = None
    closed_at: Optional[datetime] = None
    realized_pnl: Optional[float] = None

    @property
    def is_open(self) -> bool:
        return self.exit_price is None

    @property
    def is_closed(self) -> bool:
        return self.exit_price is not None

    def close(self, exit_price: float, realized_pnl: float):
        """
        Close the position and store final realized PnL.
        """
        self.exit_price = exit_price
        self.closed_at = datetime.now(timezone.utc)
        self.realized_pnl = realized_pnl
