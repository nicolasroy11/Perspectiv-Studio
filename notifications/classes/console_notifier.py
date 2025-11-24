from notifications.classes.notifier import Notifier
from notifications.classes.trade_notification import TradeNotification


class ConsoleNotifier(Notifier):
    """
    A simple notifier that prints notifications to stdout.
    Perfect for dev/testing.
    """
    def send(self, notification: TradeNotification):
        print(f"[NOTIFY] {notification.event.value}: {notification.message}")
