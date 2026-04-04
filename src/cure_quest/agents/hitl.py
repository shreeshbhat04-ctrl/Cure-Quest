from sqlalchemy.orm import Session
from sqlalchemy import select

from cure_quest.adapters.ticketing import TicketingAdapter, build_ticketing_adapter
from cure_quest.db.models import ChronicCondition, EscalationCase, Notification, Prescription


class HITLAgent:
    def __init__(self, ticketing_adapter: TicketingAdapter | None = None) -> None:
        self.ticketing_adapter = ticketing_adapter or build_ticketing_adapter()

    def create_case(self, db: Session, patient_id: int, case_type: str, summary: str) -> EscalationCase:
        ticket = self.ticketing_adapter.create_review_ticket(patient_id=patient_id, summary=summary, case_type=case_type)
        case = EscalationCase(
            patient_id=patient_id,
            case_type=case_type,
            status=ticket.status,
            summary=summary,
            external_ticket_id=ticket.ticket_id,
            external_ticket_url=ticket.external_url,
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    def build_detailed_report(self, db: Session, patient_id: int, context_summary: str | None = None) -> str:
        conditions = db.scalars(select(ChronicCondition).where(ChronicCondition.patient_id == patient_id)).all()
        prescriptions = db.scalars(select(Prescription).where(Prescription.patient_id == patient_id)).all()
        notifications = db.scalars(select(Notification).where(Notification.patient_id == patient_id)).all()

        condition_lines = ", ".join(f"{item.name} ({item.condition_type})" for item in conditions) or "No conditions recorded."
        prescription_lines = (
            "; ".join(
                f"{item.medication_name} {item.dosage or ''} [{item.review_status}]".strip()
                for item in prescriptions
            )
            or "No prescriptions recorded."
        )
        notification_lines = (
            "; ".join(f"{item.message_type}:{item.delivery_status}" for item in notifications[-5:])
            or "No recent patient communications."
        )

        sections = [
            f"Patient ID: {patient_id}",
            f"Clinical context: {condition_lines}",
            f"Medication history: {prescription_lines}",
            f"Communication history: {notification_lines}",
        ]
        if context_summary:
            sections.append(f"Latest concern: {context_summary}")
        return "\n".join(sections)
