from sqlalchemy.orm import Session

from cure_quest.adapters.ticketing import RoutineTask
from cure_quest.adapters.notifications import MockNotificationAdapter
from cure_quest.services.brain import BrainCondition, BrainPatientProfile
from cure_quest.services.model_routing import ModelRoutingService
from cure_quest.db.models import Notification


class CommunicationsAgent:
    def __init__(self, notification_adapter: MockNotificationAdapter | None = None) -> None:
        self.notification_adapter = notification_adapter or MockNotificationAdapter()
        self.model_routing = ModelRoutingService()

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

    def compose_daily_checkin(
        self,
        profile: BrainPatientProfile | None,
        conditions: list[BrainCondition],
        routine_tasks: list[RoutineTask],
    ) -> str:
        patient_name = profile.full_name if profile is not None else "there"
        condition_summary = ", ".join(condition.name for condition in conditions[:3]) if conditions else "your current care plan"
        pending_tasks = [task.name for task in routine_tasks if not task.completed][:3]
        task_summary = "; ".join(pending_tasks) if pending_tasks else "no pending routine tasks today"
        return (
            f"Hi {patient_name}, just checking in on your day. "
            f"I'm keeping an eye on {condition_summary}. "
            f"Today's routine focus is: {task_summary}. "
            "Let me know how you're feeling and whether you took your medicines."
        )

    def build_conversation_plan(self, message: str) -> dict[str, object]:
        route = self.model_routing.route_general_conversation(message)
        return {
            "message": message,
            "route_type": route["route_type"],
            "primary_model": route["primary_model"],
            "support_model": route["support_model"],
            "reason": route["reason"],
            "suggested_response_style": "calm, reassuring, and patient-friendly",
            "execution_plan": route["execution_plan"],
        }
