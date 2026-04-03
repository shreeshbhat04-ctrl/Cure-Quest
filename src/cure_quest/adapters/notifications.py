from dataclasses import dataclass


@dataclass
class NotificationResult:
    channel: str
    delivery_status: str


class MockNotificationAdapter:
    def send(self, channel: str, message_body: str) -> NotificationResult:
        _ = message_body
        return NotificationResult(channel=channel, delivery_status="sent")
