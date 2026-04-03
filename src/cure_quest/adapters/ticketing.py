from dataclasses import dataclass
from datetime import date
from uuid import uuid4

import httpx

from cure_quest.config import get_settings


@dataclass
class TicketResult:
    ticket_id: str
    status: str
    external_url: str | None = None


class TicketingAdapter:
    def create_review_ticket(self, patient_id: int, summary: str, case_type: str) -> TicketResult:
        raise NotImplementedError


class MockTicketingAdapter(TicketingAdapter):
    def create_review_ticket(self, patient_id: int, summary: str, case_type: str) -> TicketResult:
        _ = (patient_id, summary, case_type)
        ticket_id = f"CQ-{str(uuid4())[:8].upper()}"
        return TicketResult(ticket_id=ticket_id, status="created")


class AsanaTicketingAdapter(TicketingAdapter):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://app.asana.com/api/1.0"

    def create_review_ticket(self, patient_id: int, summary: str, case_type: str) -> TicketResult:
        if not self.settings.asana_access_token or not self.settings.asana_project_gid:
            raise ValueError("ASANA_ACCESS_TOKEN and ASANA_PROJECT_GID must be configured.")

        task_name = f"[REVIEW REQUIRED] Patient {patient_id}"
        notes = f"Case type: {case_type}\n\nSummary:\n{summary}"
        data: dict[str, object] = {
            "name": task_name,
            "notes": notes,
            "projects": [self.settings.asana_project_gid],
        }

        if self.settings.asana_assignee_gid:
            data["assignee"] = self.settings.asana_assignee_gid
        if self.settings.asana_task_due_on:
            data["due_on"] = self.settings.asana_task_due_on
        elif case_type == "doctor_review":
            data["due_on"] = date.today().isoformat()

        headers = {
            "Authorization": f"Bearer {self.settings.asana_access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{self.base_url}/tasks",
                json={"data": data},
                headers=headers,
            )
            response.raise_for_status()
            payload = response.json()["data"]

        task_gid = payload["gid"]
        permalink = payload.get("permalink_url")
        return TicketResult(ticket_id=task_gid, status="created", external_url=permalink)


def build_ticketing_adapter() -> TicketingAdapter:
    settings = get_settings()
    if settings.asana_access_token and settings.asana_project_gid:
        return AsanaTicketingAdapter()
    return MockTicketingAdapter()
