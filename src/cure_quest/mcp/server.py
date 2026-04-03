from mcp.server.fastmcp import FastMCP

from cure_quest.db.session import SessionLocal
from cure_quest.services.emergency import detect_emergency
from cure_quest.services.brain import BrainService

mcp = FastMCP("CureQuestLocal", json_response=True)
brain_service = BrainService()


@mcp.tool()
def ping() -> dict[str, str]:
    """Return a deterministic connectivity response."""
    return {"status": "ok", "server": "CureQuestLocal"}


@mcp.tool()
def check_emergency(text: str) -> dict[str, bool]:
    """Run the emergency intercept rules against text."""
    return {"emergency_detected": detect_emergency(text)}


@mcp.tool()
def patient_context_summary(patient_name: str, conditions: list[str]) -> dict[str, str]:
    """Build a compact deterministic summary for smoke tests."""
    joined = ", ".join(conditions) if conditions else "no recorded conditions"
    return {"summary": f"{patient_name} has {joined}."}


@mcp.tool()
def brain_healthcheck() -> dict[str, str]:
    """Check DB connectivity for the shared patient brain."""
    with SessionLocal() as db:
        return brain_service.healthcheck(db)


@mcp.tool()
def brain_get_patient_profile(patient_id: int) -> dict:
    """Fetch a patient profile from the shared brain store."""
    with SessionLocal() as db:
        profile = brain_service.get_patient_profile(db, patient_id)
        return {"profile": None if profile is None else profile.to_dict()}


@mcp.tool()
def brain_get_relevant_conditions(patient_id: int) -> dict:
    """Fetch temporal-memory filtered conditions for a patient."""
    with SessionLocal() as db:
        conditions = brain_service.get_relevant_conditions(db, patient_id)
        return {"conditions": [condition.to_dict() for condition in conditions]}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
