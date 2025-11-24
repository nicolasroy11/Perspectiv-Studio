import boto3
import runtime_settings as rs

from notifications.classes.notifier import Notifier
from notifications.classes.trade_notification import TradeNotification


class AwsSmsNotifier(Notifier):
    """
    Sends SMS messages using AWS SNS.
    Requires:
        - rs.AWS_REGION
        - rs.NOTIFICATION_PHONE_NUMBER  (E.164 format: +1xxxxxxxxxx)
        - AWS credentials in environment (IAM user or role)
    """

    def __init__(self, region: str = rs.AWS_REGION, phone_number: str = rs.NOTIFICATION_PHONE_NUMBER):
        self.region = region or rs.AWS_REGION
        self.phone_number = phone_number or rs.NOTIFICATION_PHONE_NUMBER

        self.sns = boto3.client("sns", region_name=self.region)

    def send(self, notification: TradeNotification):
        self.sns.publish(
            PhoneNumber=self.phone_number,
            Message=notification.message
        )


from notifications.classes.aws_sms_notifier import AwsSmsNotifier
from notifications.classes.trade_notification import TradeNotification
from notifications.classes.trade_event import TradeEvent

notifier = AwsSmsNotifier()

test_note = TradeNotification(
    event=TradeEvent.ANCHOR_ENTRY,
    message="Test SMS: Anchor entry triggered at 1.10234"
)

notifier.send(test_note)
