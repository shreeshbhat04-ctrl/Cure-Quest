from sqlalchemy.orm import Session

from cure_quest.adapters.ticketing import MockTicketingAdapter
from cure_quest.db.models import EscalationCase


class HITLAgent:
    def __init__(self, ticketing_adapter: MockTicketingAdapter | None = None) -> None:
        self.ticketing_adapter = ticketing_adapter or MockTicketingAdapter()

    def create_case(self, db: Session, patient_id: int, case_type: str, summary: str) -> EscalationCase:
        ticket = self.ticketing_adapter.create_review_ticket(summary=summary)
        case = EscalationCase(
            patient_id=patient_id,
            case_type=case_type,
            status=ticket.status,
            summary=summary,
            external_ticket_id=ticket.ticket_id,
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case
