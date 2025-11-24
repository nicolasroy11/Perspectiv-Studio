from twilio.rest import Client
from notifications.classes.notifier import Notifier
from notifications.classes.trade_notification import TradeNotification
import runtime_settings as rs


class TwilioSmsNotifier(Notifier):
    def __init__(self):
        self.client = Client(rs.TWILIO_ACCOUNT_SID, rs.TWILIO_AUTH_TOKEN)
        self.from_number = rs.TWILIO_FROM_NUMBER
        self.to_number = rs.NOTIFICATION_PHONE_NUMBER

    def send(self, notification: TradeNotification):
        self.client.messages.create(
            body=notification.message,
            from_=self.from_number,
            to=self.to_number
        )
