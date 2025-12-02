from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal

from utils.time import ms_to_dt

Side = Literal["buy", "sell"]

@dataclass
class Trade:
    """
    One execution / fill.

    In TL terms, this is closest to a 'deal' or 'trade fill' rather than
    a logical cycle. It is intentionally environment-agnostic.
    """
    id: str                                 # trade id
    custom_id: str                          # formulated and assigned by this program
    status: str
    cycle_id: Optional[str]                 # logical cycle this belongs to
    symbol: str                             # e.g. "EURUSD"
    side: Side                              # "buy" or "sell"
    lot_size: float                         # in standard lots (e.g. 1.0 = 100k)

    executed_price: float                      # execution price
    open_time: datetime

    tp_price: Optional[float] = None
    sl_price: Optional[float] = None

    # Raw provider payload for debugging
    raw: dict = field(default_factory=dict)
    
    @staticmethod
    def from_tradelocker_order_history_row(
        row: list[str],
        field_order: list[str],
        # instrument_id_to_symbol: dict[int, str],
        # cycle_id: Optional[str] = None
    ) -> Trade:
        """
        Convert a TL orderHistory row (list of values) into a Trade object.
        """

        # 1. Turn TL flat row → dict
        raw = { field_order[i]: row[i] for i in range(len(field_order)) }

        # 2. Extract core fields safely
        trade_id = raw.get("id")  # TL sometimes uses 'id'
        strategy_id = raw.get("strategyId")
        status = raw.get("status")
        symbol = ''

        side = raw.get("side")
        qty = float(raw["filledQty"] or 0.0)

        # TL uses '0.01' to mean 0.01 lots
        lot_size = qty

        # Prices
        price = raw.get("price") if not raw.get("avgPrice") else raw.get("avgPrice")
        executed_price = float(price)

        # Timestamps
        open_time = ms_to_dt(raw.get("createdDate"))

        # TP/SL
        tp_price = float(raw["takeProfit"]) if raw.get("takeProfit") else None
        sl_price = float(raw["stopLoss"]) if raw.get("stopLoss") else None

        # Pending vs filled
        status = raw.get("status", "").lower()

        # RETURN Trade dataclass
        return Trade(
            id=trade_id,
            status=status,
            cycle_id=0,
            symbol=symbol,
            side=side,
            lot_size=lot_size,
            executed_price=executed_price,
            open_time=open_time,
            tp_price=tp_price,
            sl_price=sl_price,
            custom_id=strategy_id,
            raw=raw
        )
        
    @staticmethod
    def _extract_position_depth(trade: Trade) -> int:
        """
        Extract the depth from strategyId.
        Expected format:  "<cycle_id>_<depth>"
        Example: "RSILR_2025-11-29T22:55:18_3"
        """
        malformed_value = -1
        sid = trade.custom_id
        if not sid or "_" not in sid:
            return malformed_value  # fallback, treat as anchor
        
        # depth is always the last segment
        try:
            depth_str = sid.rsplit("_", 1)[1]
            return int(depth_str)
        except Exception:
            return malformed_value
