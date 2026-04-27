# Cure-Quest Connection Architecture

This document focuses on infrastructure and external connection wiring for Cure-Quest.

Out of scope for this phase:

- multimodal model integration
- agent orchestration logic
- agent trigger rules
- workflow automation depth

The goal is to make every external connection path explicit so implementation can proceed safely.

## 1. Core runtime surfaces

There are three runtime entrypoints in the project today:

1. FastAPI application
2. Google ADK web agent
3. Local MCP server

These sit on top of one shared database layer that should ultimately point to AlloyDB.

## 2. Connection map

### A. Product API path

```text
Frontend or API client
  -> FastAPI app
  -> app services / agents
  -> Brain gateway
     -> direct mode: SQLAlchemy -> Database
     -> mcp mode: MCP client -> local MCP server -> Brain service -> Database
```

Use this path for:

- patient intake endpoints
- prescription scan endpoints
- alternative lookup endpoints
- escalation endpoints
- notification endpoints

### B. ADK demo path

```text
Google ADK Web UI
  -> cure_quest_agent
  -> root_agent
  -> MCP toolset
  -> local MCP server
  -> Brain service / DB tools
  -> Database
```

Use this path for:

- manual testing in ADK web
- validating tool discovery
- validating Gemini-to-tool communication
- validating DB-backed patient context access

### C. MCP-only validation path

```text
Smoke test script
  -> stdio MCP client
  -> local MCP server
  -> Brain service
  -> Database
```

Use this path for:

- connectivity checks
- tool contract checks
- DB access validation
- transport debugging

## 3. Current external connection categories

### FastAPI server

Purpose:

- primary backend HTTP API for the app
- local workflow testing
- future frontend/web/mobile integration target

Current implementation:

- runs from `cure_quest.app:app`
- routes live under `src/cure_quest/api`
- database bootstraps during app startup

Required local connection:

- database through `DATABASE_URL`

Future external connections:

- frontend client
- auth provider
- task/ticket system
- notification provider
- EHR/FHIR integration

### Google ADK web server

Purpose:

- testing the ADK agent in Google’s web UI
- validating tool-based interactions before deeper orchestration work

Current implementation:

- dedicated ADK web package lives in `adk_agents/cure_quest_agent`
- wrapper imports `root_agent` from `src/cure_quest/adk/agent.py`
- ADK agent uses `McpToolset` over stdio to talk to the local MCP server

Required external connections:

- Gemini model access through `GOOGLE_API_KEY`
- local MCP server process spawned by ADK

Important note:

- ADK web should point to `adk_agents`, not `src/cure_quest`
- Otherwise, normal app folders are incorrectly treated as agents

### Local MCP server

Purpose:

- standard tool boundary between agents and the shared patient brain
- local development stand-in for more production-like tool routing

Current implementation:

- served by `python -m cure_quest.mcp.server`
- exposes deterministic tools and DB-backed brain tools

Current tool groups:

- utility tools: `ping`, `check_emergency`, `patient_context_summary`
- brain tools: `brain_healthcheck`, `brain_get_patient_profile`, `brain_get_relevant_conditions`

Required external connections:

- database through SQLAlchemy session layer

Current external MCP servers:

- `@modelcontextprotocol/server-google-maps` for pharmacy and location services (requires `GOOGLE_MAPS_API_KEY`)

Future external connections:

- MCP Toolbox for AlloyDB
- ticketing MCP servers
- Gmail / Calendar / Asana style tools

### Database / AlloyDB

Purpose:

- source of truth for patient memory and application state
- shared “brain” store behind both API and MCP paths

Current implementation:

- SQLAlchemy models in `src/cure_quest/db/models.py`
- local default database is SQLite
- schema is Postgres-compatible

Target production-like path:

- set `DATABASE_URL` to an AlloyDB/Postgres connection string
- keep app code unchanged
- rerun bootstrap and connection tests

Current DB entities:

- `patients`
- `chronic_conditions`
- `prescriptions`
- `medication_events`
- `escalation_cases`
- `notifications`

## 4. Recommended connection sequence

Wire connections in this order:

1. Database connection
2. FastAPI to database
3. MCP server to database
4. ADK agent to MCP server
5. ADK web UI to ADK agent
6. External product integrations one by one

This order keeps failure isolation simple.

## 5. Direct vs MCP brain modes

### `BRAIN_GATEWAY_MODE=direct`

Use when:

- validating schema
- validating API endpoints quickly
- debugging DB logic

Path:

```text
API -> Brain service -> SQLAlchemy -> DB
```

### `BRAIN_GATEWAY_MODE=mcp`

Use when:

- validating actual tool transport
- preparing the eventual agent-driven architecture
- testing ADK and MCP together

Path:

```text
API or ADK -> MCP -> Brain tools -> DB
```

Recommended local progression:

- get `direct` working first
- switch to `mcp` once the DB is stable

## 6. External integrations to wire after the core stack

Treat these as separate workstreams after API, ADK, MCP, and AlloyDB are stable.

### Notifications

Candidate connections:

- Gmail API
- SendGrid
- Twilio
- Firebase messaging

Current state:

- mock adapter only

### Doctor review / tickets

Candidate connections:

- Asana
- Jira
- Linear

Current state:

- mock ticket adapter only

### Pharmacy inventory

Candidate connections:

- custom MCP server
- mock HTTP service
- partner pharmacy API

Current state:

- mock formulary adapter only

### EHR / FHIR

Candidate connections:

- Cloud Healthcare API
- external FHIR endpoint
- internal hospital FHIR service

Current state:

- not wired yet

## 7. Minimum "all core connections are working" definition

You can consider the infrastructure phase complete when all of these are true:

1. FastAPI starts and serves endpoints locally.
2. `test_database_connection.py` passes against the target DB.
3. `test_mcp_connection.py` passes.
4. `BRAIN_GATEWAY_MODE=mcp` works for API reads.
5. `adk web` launches from `adk_agents`.
6. The ADK UI can call at least one MCP brain tool successfully.
7. Switching from SQLite to AlloyDB only requires env/config changes, not code rewrites.
