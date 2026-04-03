from sqlalchemy.orm import Session

from cure_quest.adapters.notifications import MockNotificationAdapter
from cure_quest.db.models import Notification


class CommunicationsAgent:
    def __init__(self, notification_adapter: MockNotificationAdapter | None = None) -> None:
        self.notification_adapter = notification_adapter or MockNotificationAdapter()

    def notify(self, db: Session, patient_id: int, channel: str, message_type: str, message_body: str) -> Notification:
        result = self.notification_adapter.send(channel=channel, message_body=message_body)
        notification = Notification(
            patient_id=patient_id,
            channel=result.channel,
            message_type=message_type,
            body=message_body,
            delivery_status=result.delivery_status,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
