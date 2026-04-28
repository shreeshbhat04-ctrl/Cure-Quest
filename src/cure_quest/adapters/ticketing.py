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
    source: str = "Asana"
    title: str | None = None
    short_summary: str | None = None
    full_details: str | None = None
    due_at: str | None = None
    due_on: str | None = None
    notes: str | None = None
    assignee_name: str | None = None
    assignee_gid: str | None = None
    permalink_url: str | None = None


@dataclass
class AsanaWorkspaceUser:
    gid: str
    name: str
    email: str | None = None


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

    def list_workspace_users(self, workspace_gid: str | None = None) -> list[dict[str, str | None]]:
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
                title="Morning medication reminder",
                short_summary="Morning dose check-in.",
                full_details="Check whether the patient took the morning dose.",
                due_at=date.today().isoformat(),
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
                title="Follow-up symptom check",
                short_summary="Brief symptom follow-up is due today.",
                full_details="Ask how the patient is feeling today.",
                due_at=date.today().isoformat(),
                due_on=date.today().isoformat(),
                notes="Ask how the patient is feeling today.",
                assignee_name="Care Coordinator",
                assignee_gid=None,
                permalink_url=None,
            ),
        ]

    def list_workspace_users(self, workspace_gid: str | None = None) -> list[dict[str, str | None]]:
        _ = workspace_gid
        return [
            {
                "gid": "mock-doctor-1",
                "name": "Dr surgeon",
                "email": "sreeshhb@gmail.com",
            }
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
                    title=item.get("name", ""),
                    short_summary=_short_summary(item.get("notes"), item.get("name", "")),
                    full_details=item.get("notes"),
                    due_at=item.get("due_on"),
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

    def list_workspace_users(self, workspace_gid: str | None = None) -> list[dict[str, str | None]]:
        if not self.settings.asana_access_token:
            raise ValueError("ASANA_ACCESS_TOKEN must be configured.")

        resolved_workspace_gid = workspace_gid or self.settings.asana_workspace_gid
        if not resolved_workspace_gid:
            raise ValueError("ASANA_WORKSPACE_GID must be configured or provided.")

        headers = {
            "Authorization": f"Bearer {self.settings.asana_access_token}",
            "Accept": "application/json",
        }
        params = {"opt_fields": "name,email"}

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(
                    f"{self.base_url}/workspaces/{resolved_workspace_gid}/users",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                payload = response.json()["data"]
            return [
                AsanaWorkspaceUser(
                    gid=item["gid"],
                    name=item.get("name", ""),
                    email=item.get("email"),
                ).__dict__
                for item in payload
            ]
        except Exception as error:
            logger.exception("Asana workspace user lookup failed: %s", error)
            raise


def build_ticketing_adapter() -> TicketingAdapter:
    settings = get_settings()
    if settings.asana_access_token and (settings.asana_project_gid or settings.asana_workspace_gid):
        return AsanaTicketingAdapter()
    return MockTicketingAdapter()


def _short_summary(notes: str | None, fallback: str) -> str:
    if notes:
        normalized = " ".join(notes.split())
        if len(normalized) <= 96:
            return normalized
        return normalized[:93].rstrip() + "..."
    return fallback
