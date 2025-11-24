from enum import Enum


class TradeEvent(Enum):
    ANCHOR_ENTRY = "anchor_entry"
    SCALE_IN = "scale_in"
    BASKET_UPDATE = "basket_update"
    BASKET_CLOSE = "basket_close"
