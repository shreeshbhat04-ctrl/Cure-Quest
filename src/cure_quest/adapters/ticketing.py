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
    assignee_gid: str | None = None
    permalink_url: str | None = None


class TicketingAdapter:
    def create_review_ticket(
        self,
        patient_id: int,
        summary: str,
        case_type: str,
        doctor_asana_gid: str | None = None,
        doctor_name: str | None = None,
        urgency: str | None = None,
    ) -> TicketResult:
        raise NotImplementedError

    def list_routine_tasks(self, assignee_gid: str | None = None) -> list[RoutineTask]:
        raise NotImplementedError


class MockTicketingAdapter(TicketingAdapter):
    def create_review_ticket(
        self,
        patient_id: int,
        summary: str,
        case_type: str,
        doctor_asana_gid: str | None = None,
        doctor_name: str | None = None,
        urgency: str | None = None,
    ) -> TicketResult:
        _ = (patient_id, summary, case_type, doctor_asana_gid, doctor_name, urgency)
        ticket_id = f"CQ-{str(uuid4())[:8].upper()}"
        return TicketResult(ticket_id=ticket_id, status="created")

    def list_routine_tasks(self, assignee_gid: str | None = None) -> list[RoutineTask]:
        _ = assignee_gid
        return [
            RoutineTask(
                task_id="mock-1",
                name="Morning medication reminder",
                completed=False,
                due_on=date.today().isoformat(),
                notes="Check whether the patient took the morning dose.",
                assignee_name="Care Coordinator",
                assignee_gid=None,
                permalink_url=None,
            ),
            RoutineTask(
                task_id="mock-2",
                name="Follow-up symptom check",
                completed=False,
                due_on=date.today().isoformat(),
                notes="Ask how the patient is feeling today.",
                assignee_name="Care Coordinator",
                assignee_gid=None,
                permalink_url=None,
            ),
        ]


class AsanaTicketingAdapter(TicketingAdapter):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = "https://app.asana.com/api/1.0"
        self._mock = MockTicketingAdapter()

    def create_review_ticket(
        self,
        patient_id: int,
        summary: str,
        case_type: str,
        doctor_asana_gid: str | None = None,
        doctor_name: str | None = None,
        urgency: str | None = None,
    ) -> TicketResult:
        if not self.settings.asana_access_token or not self.settings.asana_project_gid:
            raise ValueError("ASANA_ACCESS_TOKEN and ASANA_PROJECT_GID must be configured.")

        task_name = f"[REVIEW REQUIRED] Patient {patient_id}"
        note_lines = [
            f"Case type: {case_type}",
            f"Patient ID: {patient_id}",
        ]
        if doctor_name:
            note_lines.append(f"Doctor: {doctor_name}")
        if urgency:
            note_lines.append(f"Urgency: {urgency}")
        note_lines.extend(["", "Summary:", summary])
        notes = "\n".join(note_lines)
        data: dict[str, object] = {
            "name": task_name,
            "notes": notes,
            "projects": [self.settings.asana_project_gid],
        }

        assignee_gid = doctor_asana_gid or self.settings.asana_assignee_gid
        if assignee_gid:
            data["assignee"] = assignee_gid
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
            return self._mock.create_review_ticket(
                patient_id=patient_id,
                summary=summary,
                case_type=case_type,
                doctor_asana_gid=doctor_asana_gid,
                doctor_name=doctor_name,
                urgency=urgency,
            )

    def list_routine_tasks(self, assignee_gid: str | None = None) -> list[RoutineTask]:
        if not self.settings.asana_access_token or not self.settings.asana_project_gid:
            raise ValueError("ASANA_ACCESS_TOKEN and ASANA_PROJECT_GID must be configured.")

        headers = {
            "Authorization": f"Bearer {self.settings.asana_access_token}",
            "Accept": "application/json",
        }
        params = {
            "completed_since": "now",
            "opt_fields": "name,completed,due_on,notes,assignee.gid,assignee.name,permalink_url",
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
                    assignee_gid=(item.get("assignee") or {}).get("gid"),
                    permalink_url=item.get("permalink_url"),
                )
                for item in payload
            ]
            filter_assignee_gid = assignee_gid or self.settings.asana_assignee_gid
            if filter_assignee_gid:
                tasks = [task for task in tasks if task.assignee_gid == filter_assignee_gid]
            return tasks
        except Exception as error:
            logger.warning("Asana routine fetch failed, falling back to mock tasks: %s", error)
            return self._mock.list_routine_tasks(assignee_gid=assignee_gid)


def build_ticketing_adapter() -> TicketingAdapter:
    settings = get_settings()
    if settings.asana_access_token and settings.asana_project_gid:
        return AsanaTicketingAdapter()
    return MockTicketingAdapter()
