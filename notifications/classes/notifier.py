from abc import ABC, abstractmethod
from notifications.classes.trade_notification import TradeNotification


class Notifier(ABC):
    """
    Base interface for all notifier types (SMS, email, webhook, logging, etc.)
    """

    @abstractmethod
    def send(self, notification: TradeNotification):
        pass
