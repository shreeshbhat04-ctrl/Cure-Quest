from dataclasses import dataclass
from datetime import date
from uuid import uuid4

import httpx
import logging

from cure_quest.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TicketResult:
    ticket_id: str
    status: str
    external_url: str | None = None


@dataclass
class RoutineTask:
    task_id: str
    name: str
    completed: bool
    due_on: str | None = None
    notes: str | None = None
    assignee_name: str | None = None
    permalink_url: str | None = None


class TicketingAdapter:
    def create_review_ticket(self, patient_id: int, summary: str, case_type: str) -> TicketResult:
        raise NotImplementedError

    def list_routine_tasks(self) -> list[RoutineTask]:
        raise NotImplementedError


class MockTicketingAdapter(TicketingAdapter):
    def create_review_ticket(self, patient_id: int, summary: str, case_type: str) -> TicketResult:
        _ = (patient_id, summary, case_type)
        ticket_id = f"CQ-{str(uuid4())[:8].upper()}"
        return TicketResult(ticket_id=ticket_id, status="created")

    def list_routine_tasks(self) -> list[RoutineTask]:
        return [
            RoutineTask(
                task_id="mock-1",
                name="Morning medication reminder",
                completed=False,
                due_on=date.today().isoformat(),
                notes="Check whether the patient took the morning dose.",
                assignee_name="Care Coordinator",
                permalink_url=None,
            ),
            RoutineTask(
                task_id="mock-2",
                name="Follow-up symptom check",
                completed=False,
                due_on=date.today().isoformat(),
                notes="Ask how the patient is feeling today.",
                assignee_name="Care Coordinator",
                permalink_url=None,
            ),
        ]


class AsanaTicketingAdapter(TicketingAdapter):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://app.asana.com/api/1.0"
        self._mock = MockTicketingAdapter()

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

        try:
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
        except Exception as error:
            logger.warning("Asana ticket creation failed, falling back to mock ticket: %s", error)
            return self._mock.create_review_ticket(patient_id=patient_id, summary=summary, case_type=case_type)

    def list_routine_tasks(self) -> list[RoutineTask]:
        if not self.settings.asana_access_token or not self.settings.asana_project_gid:
            raise ValueError("ASANA_ACCESS_TOKEN and ASANA_PROJECT_GID must be configured.")

        headers = {
            "Authorization": f"Bearer {self.settings.asana_access_token}",
            "Accept": "application/json",
        }
        params = {
            "completed_since": "now",
            "opt_fields": "name,completed,due_on,notes,assignee.name,permalink_url",
            "limit": 20,
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(
                    f"{self.base_url}/projects/{self.settings.asana_project_gid}/tasks",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                payload = response.json()["data"]
            tasks = [
                RoutineTask(
                    task_id=item["gid"],
                    name=item.get("name", ""),
                    completed=item.get("completed", False),
                    due_on=item.get("due_on"),
                    notes=item.get("notes"),
                    assignee_name=(item.get("assignee") or {}).get("name"),
                    permalink_url=item.get("permalink_url"),
                )
                for item in payload
            ]
            if self.settings.asana_assignee_gid:
                tasks = [task for task in tasks if task.assignee_name]
            return tasks
        except Exception as error:
            logger.warning("Asana routine fetch failed, falling back to mock tasks: %s", error)
            return self._mock.list_routine_tasks()


def build_ticketing_adapter() -> TicketingAdapter:
    settings = get_settings()
    if settings.asana_access_token and settings.asana_project_gid:
        return AsanaTicketingAdapter()
    return MockTicketingAdapter()
