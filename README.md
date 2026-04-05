# Cure-Quest

Cure-Quest is the starter codebase for a chronic-care AI copilot demo. This first scaffold focuses on local development setup, a thin FastAPI app, a local MCP server, and a Google ADK agent wired to that MCP server.

## What is included

- FastAPI application with `health`, `demo`, and placeholder workflow endpoints
- Local MCP server with deterministic tools and DB-backed "brain" tools
- Google ADK agent definition configured to load tools from the local MCP server over stdio
- SQLAlchemy models for the first demo entities
- PowerShell and Python scripts to set up the environment and smoke-test DB/MCP/ADK wiring

## Quick start

1. Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -e .[dev]
```

3. Copy the environment file and update values as needed:

```powershell
Copy-Item .env.example .env
```

4. Run the API:

```powershell
uvicorn cure_quest.app:app --reload
```

5. Smoke-test MCP connectivity:

```powershell
python scripts/test_mcp_connection.py
```

6. Smoke-test database connectivity:

```powershell
python scripts/test_database_connection.py
```

7. Smoke-test ADK setup:

```powershell
python scripts/test_adk_agent.py
```

8. Inspect Asana connectivity and IDs:

```powershell
python scripts/test_asana_connection.py
```

9. Inspect Google Drive connectivity:

```powershell
python scripts/test_drive_connection.py
```

10. Inspect Google Calendar connectivity:

```powershell
python scripts/test_calendar_connection.py
```

## Extra integrations

- `POST /documents/upload` uploads a local file to Google Drive and can attach it to a prescription record.
- `POST /calendar/events` creates a Google Calendar event.
- `POST /drug/label` looks up drug label data from openFDA.
- `POST /pharmacy/search` searches nearby pharmacies using Google Places.
- `POST /patient/escalate` can now also upload a document, create a follow-up calendar event, and store external links on the escalation case.

## Orchestration agent surfaces

- `GET /orchestration/check-in/{patient_id}` builds a patient-facing daily check-in using profile, conditions, and routine tasks.
- `GET /orchestration/routine/{patient_id}` returns the routine/reminder task snapshot, currently backed by Asana or mock tasks.
- `POST /orchestration/hitl-report` builds a detailed doctor report and can optionally create a real escalation case.
- `POST /orchestration/diet-support` builds medication-aware diet guidance and pharmacy context.
- `POST /orchestration/document-pipeline` describes the OCR + storage pipeline for uploaded medical documents.
- `POST /orchestration/run-document-flow` runs the end-to-end document intake workflow automatically.
- `GET /orchestration/routine-automation/{patient_id}` evaluates routine risk and can prepare HITL escalation.
- `GET /orchestration/manifest/{patient_id}` shows the current five-agent orchestration structure and model assignments.

## Medical model execution

The repo now supports two layers for medical-model work:

- routing-only orchestration that decides when `MedGemma`, `MedSigLIP`, or `Gemini 3.1 Flash` should be used
- optional Hugging Face execution for `MedGemma` and `MedSigLIP`

To enable the Hugging Face backend:

```powershell
pip install -e .[hf]
```

You will also need a PyTorch install that matches your machine. Follow the selector at:

- https://pytorch.org/get-started/locally/

Then set these in `.env`:

```env
MEDICAL_MODEL_BACKEND=huggingface
HUGGINGFACE_HUB_TOKEN=
MEDGEMMA_MODEL_ID=google/medgemma-1.5-4b-it
MEDSIGLIP_MODEL_ID=google/medsiglip-448
```

Useful endpoints:

- `POST /medical-models/medgemma`
- `POST /medical-models/medsiglip/classify`
- `POST /medical-memory/store`
- `POST /medical-memory/search`

If `use_live_embedding=true` is passed to `/medical-memory/store`, the app will try to generate a real `MedSigLIP` embedding before saving the memory.

## BigQuery and AlloyDB setup helpers

- `python scripts/setup_bigquery_table.py`
- `python scripts/test_bigquery_logging.py`
- `python scripts/setup_alloydb_vector.py`
- `python scripts/print_alloydb_proxy_command.py`

These helpers prepare the analytics table and pgvector-compatible storage when your environment is pointed at BigQuery and AlloyDB/Postgres.

## Brain architecture

The project now supports two brain gateway modes:

- `direct`: agents call a shared `BrainService` directly through SQLAlchemy. This is the easiest local dev path.
- `mcp`: agents call the MCP server, and the MCP server reads from the same DB. This gives you the intended `agent -> MCP -> DB/AlloyDB` flow.

Set `BRAIN_GATEWAY_MODE=mcp` in `.env` when you want the full transport path.

## AlloyDB direction

- The current schema is Postgres-compatible and can be pointed at AlloyDB through `DATABASE_URL`.
- A starter MCP Toolbox config lives at `toolbox/tools.yaml.example`.
- For a real AlloyDB setup, create the database first, then set `DATABASE_URL=postgresql+psycopg://...` and rerun the smoke tests.
- If you use AlloyDB Auth Proxy, set:

```env
ALLOYDB_PROJECT=your-gcp-project
ALLOYDB_REGION=us-central1
ALLOYDB_CLUSTER=your-cluster
ALLOYDB_INSTANCE=your-instance
ALLOYDB_USE_AUTH_PROXY=true
ALLOYDB_AUTH_PROXY_HOST=127.0.0.1
ALLOYDB_AUTH_PROXY_PORT=5432
ALLOYDB_DATABASE=curequest
ALLOYDB_USER=postgres
ALLOYDB_PASSWORD=your-password
```

- Then run `python scripts/print_alloydb_proxy_command.py`, start the proxy in a separate terminal, and rerun:

```powershell
python scripts/test_database_connection.py
python scripts/setup_alloydb_vector.py
```

## Project layout

```text
frontend/       Vite frontend for the four-screen Cure-Quest UI
src/cure_quest/
  api/          HTTP routes and request/response models
  agents/       Domain agents used by the orchestrator
  adapters/     Mock external integrations and future MCP boundaries
  db/           Database session setup and SQLAlchemy models
  demo_ui/      Minimal HTML dashboard
  mcp/          Local MCP server
  adk/          Google ADK agent definition
  services/     Shared orchestration and safety logic
scripts/        Setup and smoke-test helpers
tests/          Basic unit tests
```

## Notes

- The default database is SQLite for friction-free local bootstrapping, but the schema is SQLAlchemy-based so it can be pointed at Postgres or AlloyDB with `DATABASE_URL`.
- The MCP server is local and deterministic by design so we can verify transport and tool discovery before adding real clinical logic.
- The ADK agent requires a valid `GOOGLE_API_KEY` before model-backed runs will work.
- Real Asana ticket creation turns on automatically when `ASANA_ACCESS_TOKEN` and `ASANA_PROJECT_GID` are set.
- The official frontend now lives in `frontend/` and talks directly to the FastAPI backend.
