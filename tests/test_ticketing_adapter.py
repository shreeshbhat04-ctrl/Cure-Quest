import httpx

from cure_quest.adapters.ticketing import AsanaTicketingAdapter


class FailingClient:
    def __init__(self, *args, **kwargs) -> None:
        _ = args, kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def get(self, *args, **kwargs):
        _ = args, kwargs
        raise httpx.ConnectError("Asana unavailable")

    def post(self, *args, **kwargs):
        _ = args, kwargs
        raise httpx.ConnectError("Asana unavailable")


def test_asana_list_tasks_falls_back_to_mock(monkeypatch) -> None:
    monkeypatch.setattr("cure_quest.adapters.ticketing.httpx.Client", FailingClient)

    adapter = AsanaTicketingAdapter()
    adapter.settings.asana_access_token = "token"
    adapter.settings.asana_project_gid = "project"

    tasks = adapter.list_routine_tasks()

    assert len(tasks) >= 1
    assert tasks[0].task_id.startswith("mock-")


def test_asana_create_ticket_falls_back_to_mock(monkeypatch) -> None:
    monkeypatch.setattr("cure_quest.adapters.ticketing.httpx.Client", FailingClient)

    adapter = AsanaTicketingAdapter()
    adapter.settings.asana_access_token = "token"
    adapter.settings.asana_project_gid = "project"

    ticket = adapter.create_review_ticket(patient_id=2, summary="Needs review", case_type="doctor_review")

    assert ticket.ticket_id.startswith("CQ-")
    assert ticket.status == "created"
