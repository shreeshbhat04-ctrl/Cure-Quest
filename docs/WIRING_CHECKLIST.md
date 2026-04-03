# Cure-Quest Wiring Checklist

This checklist is the practical setup guide for API, ADK web, MCP, and AlloyDB.

It intentionally excludes:

- multimodal ingestion
- orchestration decisions
- trigger logic
- model quality work

## 1. Environment variables

Use `.env` as the single local source of truth.

### Required now

```env
APP_NAME=Cure-Quest
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=sqlite:///./cure_quest.db
BRAIN_GATEWAY_MODE=direct
GOOGLE_API_KEY=your_key_here
ADK_MODEL=gemini-2.5-pro
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=-m cure_quest.mcp.server
```

### Required when moving to AlloyDB

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/cure_quest
ALLOYDB_PROJECT=your-gcp-project
ALLOYDB_REGION=your-region
ALLOYDB_CLUSTER=your-cluster
ALLOYDB_INSTANCE=your-instance
ALLOYDB_DATABASE=cure_quest
ALLOYDB_USER=your-user
ALLOYDB_PASSWORD=your-password
```

### Required when validating full MCP routing

```env
BRAIN_GATEWAY_MODE=mcp
```

## 2. API server wiring

### Purpose

- confirm the app boots
- confirm DB schema initializes
- confirm HTTP routes can read and write state

### Command

```powershell
uvicorn cure_quest.app:app --reload
```

### Success criteria

- `GET /health` returns success
- patient intake works
- alternative lookup works
- no DB connection error on startup

### If it fails

Check:

- `DATABASE_URL`
- virtual environment activation
- package install state
- whether the database is reachable

## 3. Database wiring

### Local smoke test

```powershell
python scripts/test_database_connection.py
```

### Seed demo data

```powershell
python scripts/seed_demo_patient.py
```

### Success criteria

- the script prints `STATUS ok`
- the seed script creates a patient id

### SQLite phase

Use SQLite while shaping the contracts.

### AlloyDB phase

Move to AlloyDB once API + MCP contracts are stable.

Recommended steps:

1. Create the AlloyDB database.
2. Update `DATABASE_URL`.
3. Rerun the database smoke test.
4. Rerun API and MCP smoke tests.

## 4. MCP server wiring

### Purpose

- ensure tool transport works
- expose DB-backed patient brain operations
- provide a stable tool interface to ADK

### Local smoke test

```powershell
python scripts/test_mcp_connection.py
```

### Current required tools

- `brain_healthcheck`
- `brain_get_patient_profile`
- `brain_get_relevant_conditions`
- `ping`
- `check_emergency`

### Success criteria

- tool list is returned
- brain healthcheck succeeds
- patient profile fetch succeeds
- relevant conditions fetch succeeds

## 5. ADK web wiring

### Correct command

Run from the repo root:

```powershell
.\.venv\Scripts\adk.exe web --port 8001 .\adk_agents
```

### Correct expected UI shape

You should see one selectable ADK package:

- `cure_quest_agent`

The actual underlying Python `root_agent` is:

- `cure_quest_root`

### Success criteria

- the web UI opens
- only the dedicated ADK agent package appears
- the agent can invoke MCP tools

### If the UI shows `adapters`, `api`, `db`, etc.

You launched ADK with the wrong root.

Do not use:

```powershell
.\.venv\Scripts\adk.exe web .\src\cure_quest
```

Use:

```powershell
.\.venv\Scripts\adk.exe web .\adk_agents
```

## 6. AlloyDB and MCP Toolbox

### Current repo status

- the application already supports Postgres-compatible SQLAlchemy connections
- a starter Toolbox config exists at `toolbox/tools.yaml.example`

### Use this when

- you want externalized DB tools
- you want Google-style Toolbox integration around AlloyDB
- you want to evolve from the local MCP server to a more database-centered tool layer

### Local prep before Toolbox

Make sure the schema and queries work against AlloyDB through `DATABASE_URL` first.

### Toolbox prep items

1. fill AlloyDB env vars
2. convert `toolbox/tools.yaml.example` into a real `tools.yaml`
3. point the Toolbox source to the real AlloyDB host
4. validate SQL tools manually

## 7. Recommended implementation order

Follow this order and do not skip ahead:

1. `python scripts/test_database_connection.py`
2. `python scripts/seed_demo_patient.py`
3. `python scripts/test_mcp_connection.py`
4. `uvicorn cure_quest.app:app --reload`
5. test `/patient/intake`
6. test `/patient/check-alternatives`
7. switch `BRAIN_GATEWAY_MODE` from `direct` to `mcp`
8. rerun API tests
9. launch `adk web`
10. validate ADK -> MCP -> DB path
11. replace SQLite with AlloyDB
12. rerun everything

## 8. What not to wire yet

Leave these out for now:

- multimodal OCR or image pipelines
- voice or document ingestion services
- multi-agent orchestration logic
- automated escalation triggers
- production auth and compliance hardening

Those should come after the infrastructure connection layer is stable.
