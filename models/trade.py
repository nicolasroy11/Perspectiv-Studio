from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal


Side = Literal["buy", "sell"]


@dataclass
class Trade:
    """
    One execution / fill.

    In TL terms, this is closest to a 'deal' or 'trade fill' rather than
    a logical position. It is intentionally environment-agnostic.
    """
    id: str                           # TL trade / deal / order id
    position_id: Optional[str]              # logical position this belongs to
    symbol: str                             # e.g. "EURUSD"
    side: Side                              # "buy" or "sell"
    lot_size: float                         # in standard lots (e.g. 1.0 = 100k)

    entry_price: float                      # execution price
    open_time: datetime

    tp_price: Optional[float] = None
    sl_price: Optional[float] = None

    close_time: Optional[datetime] = None
    exit_price: Optional[float] = None

    realized_pnl: Optional[float] = None    # as reported by TL or backtest
    commission: Optional[float] = None
    swap: Optional[float] = None

    # Lowrider-specific metadata (purely informational)
    ladder_position: int = 0                # 0 = anchor, 1 = first rung, 2 = second, ...
    is_pending: bool = False                # True if this is a limit order not yet filled

    # Raw provider payload for debugging
    raw: dict = field(default_factory=dict)
