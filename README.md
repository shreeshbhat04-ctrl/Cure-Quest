# Cure-Quest

**An AI-powered multi-agent healthcare platform** that provides personalized chronic care management through intelligent conversational AI, real-time medication safety analysis, and transparent human-in-the-loop doctor handoffs.

Cloud Run API endpoint (for testing):
https://cure-quest-api-315569715049.us-central1.run.app

## Documentation Plan
- Source-of-truth docs: [Connection Architecture](docs/CONNECTION_ARCHITECTURE.md), [Plan 1](docs/PLAN_1_REPO_STATE_AND_MISSING_ENDPOINTS.md), [Plan 2](docs/PLAN_2_IMPLEMENTATION_CHANGE_MAP.md), [Plan 3](docs/PLAN_3_INFORMATION_NEEDED.md), [Wiring Checklist](docs/WIRING_CHECKLIST.md).
- First 3 files/folders to inspect: `docs/CONNECTION_ARCHITECTURE.md`, `docs/PLAN_1_REPO_STATE_AND_MISSING_ENDPOINTS.md`, `docs/WIRING_CHECKLIST.md`.
- First diagram to generate: **Connection Architecture Map** (FastAPI + ADK + MCP + DB).
- Estimated pass order: `1) env + bootstrap scripts, 2) backend routes/agents/adapters/MCP, 3) frontend screens/components, 4) integrations + deployment`.

## Table of Contents
- [Project Overview](#project-overview)
- [Demo Media](#demo-media)
- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Component Index](#component-index)
- [API Contracts](#api-contracts)
- [Data Flow & State Management](#data-flow--state-management)
- [AI/ML Section](#aiml-section)
- [Styling & Theming](#styling--theming)
- [Testing](#testing)
- [Build & Deployment](#build--deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Validation & Manifest](#validation--manifest)
- [VALIDATION CHECKLIST](#validation-checklist)
- [Appendix](#appendix)

## Project Overview
Cure-Quest coordinates care across multiple dimensions:
- **Voice/Chat AI** for patient questions and follow-up guidance.
- **Document upload** for prescription scans and medical artifacts.
- **HITL review** to produce doctor-ready summaries.
- **Medication reminders** and care notifications.
- **Google Workspace integration** for Drive, Calendar, Gmail, Speech, and Maps.

### Demo Story — Shreesha's Care Journey
Shreesha is a 22-year-old patient managing two chronic conditions simultaneously:
- **Atopic Eczema** (moderate to severe) — recurring flares on forearms and neck, managed with topical Clobetasol Propionate.
- **Focal Epilepsy** — diagnosed at age 19, currently controlled with Levetiracetam 500 mg twice daily.

The demo walks through drug interaction questions, document uploads, doctor handoff reports, medication reminders, and Gmail-based care summaries.

## Demo Media
- [ADK demo video (mp4)](assets/Working_adk_demo.gif)
  - Stored at `assets/Working_adk_demo.mp4` in this repo (open in GitHub if the link does not resolve in your viewer).

![ADK demo screenshot](assets/Screenshot%202026-04-27%20231914.png)
![OCR input sample](assets/Ocr_input%20(1).png)
![Latency benchmark](assets/Remarkable_latency_of_alloydb.png)

## Quick Start
### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Cloud project with APIs enabled (Drive, Calendar, Gmail, Speech, Maps)
- AlloyDB instance (or use SQLite for local dev)

### 1) Backend setup
```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]

# Configure environment
copy .env.example .env
# Edit .env with your keys

# Seed demo data
python -m cure_quest.scripts.seed

# Run API
uvicorn cure_quest.app:app --reload
```

### 2) Frontend setup
```powershell
cd frontend
npm install
npm run dev
```

---

## Tech Stack
### Core
- **Backend**: FastAPI, SQLAlchemy, Pydantic.
- **Database**: AlloyDB (PostgreSQL-compatible) for patient memory.
- **Frontend**: React, Vite, TypeScript, Framer Motion, GSAP.
- **State Management**: Zustand.

### AI & Agents
- **Gemini 3.1 Flash**: Clinical reasoning and conversational engine.
- **MedSigLIP**: Vision-based medical image classification.
- **Google ADK**: Multi-agent orchestration framework.
- **MCP (Model Context Protocol)**: Standardized tool and data access.

---

## Architecture
### High-Level Design
Cure-Quest uses a multi-agent approach where a **Root Agent** (ADK) orchestrates specialized sub-agents.

```mermaid
graph TD
    UI[React Frontend] --> API[FastAPI Backend]
    API --> ORCH[Multi-Agent Orchestrator]
    ORCH --> GEN[Gemini 3.1 Flash]
    ORCH --> MCP[MCP Server]
    MCP --> DB[(AlloyDB Patient Brain)]
    ORCH --> AGENTS[ADK Sub-Agents: Vision, Recipe, Map, etc.]
```

For detailed sequence diagrams, see [Architecture and Design](docs/ARCHITECTURE_AND_DESIGN.md).

---

## Directory Structure
```text
Cure-Quest/
├── adk_agents/          # ADK agent packages (Vision, Recipe, etc.)
├── docs/                # Architectural plans and checklists
├── frontend/            # React + Vite UI application
├── src/
│   └── cure_quest/
│       ├── adapters/    # External service connectors (Gmail, Asana, Drive)
│       ├── agents/      # Specialist agent logic
│       ├── api/         # FastAPI routes and Pydantic models
│       ├── db/          # Database models and bootstrap logic
│       ├── mcp/         # Model Context Protocol server
│       └── services/    # Business logic and model routing
├── tests/               # Unit and integration tests
└── pyproject.toml       # Python dependencies and project config
```

---

## AI/ML Section
### Model Routing
- **Gemini 3.1 Flash**: Handles complex reasoning, patient check-ins, and multi-turn chat. It leverages AlloyDB grounding to ensure responses are clinical-context-aware.
- **MedSigLIP**: Integrated for specialized image classification tasks, such as identifying prescription labels and symptom severity from photos.

### Agentic Patterns
- **Google ADK**: Enables A2A (Agent-to-Agent) delegation. For example, the Vision Agent can delegate to the Recipe Agent when it detects a dietary restriction in an uploaded document.
- **MCP (Model Context Protocol)**: Exposes "Tools" for the agents to safely interact with the database and external APIs (Maps, Calendar, etc.) in a standardized way.

---

## Testing
- **Unit Tests**: Located in `tests/`, covering adapters and core services.
- **Integration Tests**: In `tests/integration/`, validating the full path from API to Database.
- **Connectivity Tests**: `scripts/test_database_connection.py` and `scripts/test_mcp_connection.py`.

---

## VALIDATION CHECKLIST
- [ ] `.env` has `GOOGLE_API_KEY`, `GOOGLE_CLOUD_PROJECT`, and `DATABASE_URL`.
- [ ] `python -m cure_quest.scripts.seed` seeds Shreesha's care journey data.
- [ ] `uvicorn cure_quest.app:app --reload` serves `/docs` (Swagger UI).
- [ ] ADK agent launches from `adk_agents/` and communicates with the local MCP server.
- [ ] `pytest` passes with 80%+ coverage on core clinical routes.

---

## Appendix
- [Connection Architecture](docs/CONNECTION_ARCHITECTURE.md)
- [Wiring Checklist](docs/WIRING_CHECKLIST.md)
- [Cloud Run Deployment](docs/CLOUD_RUN_DEPLOYMENT.md)

