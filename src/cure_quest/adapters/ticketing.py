from dataclasses import dataclass
from uuid import uuid4


@dataclass
class TicketResult:
    ticket_id: str
    status: str


class MockTicketingAdapter:
    def create_review_ticket(self, summary: str) -> TicketResult:
        _ = summary
        ticket_id = f"CQ-{str(uuid4())[:8].upper()}"
        return TicketResult(ticket_id=ticket_id, status="created")
