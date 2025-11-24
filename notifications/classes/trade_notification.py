from dataclasses import dataclass
from notifications.classes.trade_event import TradeEvent


@dataclass
class TradeNotification:
    event: TradeEvent
    message: str
