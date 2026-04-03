import asyncio
import json
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from cure_quest.agents.intake import IntakeAgent
from cure_quest.api.models import ConditionInput, PatientIntakeRequest
from cure_quest.db.bootstrap import init_database
from cure_quest.db.session import SessionLocal


def seed_demo_patient() -> int:
    init_database()
    with SessionLocal() as db:
        patient = IntakeAgent().intake_patient(
            db,
            PatientIntakeRequest(
                full_name="MCP Demo Patient",
                preferred_language="en",
                active_conditions=[
                    ConditionInput(name="IBS", condition_type="chronic"),
                ],
            ),
        )
        return patient.id


async def main() -> None:
    patient_id = seed_demo_patient()
    repo_root = Path(__file__).resolve().parents[1]
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "cure_quest.mcp.server"],
        cwd=str(repo_root),
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS", [tool.name for tool in tools.tools])

            ping_result = await session.call_tool("ping", arguments={})
            print("PING", json.dumps(ping_result.structuredContent, indent=2))

            brain_result = await session.call_tool("brain_healthcheck", arguments={})
            print("BRAIN", json.dumps(brain_result.structuredContent, indent=2))

            profile_result = await session.call_tool(
                "brain_get_patient_profile",
                arguments={"patient_id": patient_id},
            )
            print("PROFILE", json.dumps(profile_result.structuredContent, indent=2))

            conditions_result = await session.call_tool(
                "brain_get_relevant_conditions",
                arguments={"patient_id": patient_id},
            )
            print("CONDITIONS", json.dumps(conditions_result.structuredContent, indent=2))

            emergency_result = await session.call_tool(
                "check_emergency",
                arguments={"text": "Patient says chest pain started 10 minutes ago."},
            )
            print("EMERGENCY", json.dumps(emergency_result.structuredContent, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
