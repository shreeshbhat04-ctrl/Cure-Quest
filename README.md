# Cure-Quest

An AI-assisted multi-agent prototype for medication-aware chronic care, document ingestion, human-in-the-loop (HITL) review, and clinician handoffs.

This README is a concise reference: tech stack, architecture, quick start, and validation pointers. Detailed design and runbooks live under `docs/`.

Table of contents
- Project overview
- Tech Stack
- Architecture (diagrams)
- Privacy & Trust
- Role flows
- Data flow
- AI / ML pipeline
- Quick start
- Validation checklist
- Appendix

## Tech Stack

### Frontend
- React ^18.3.1 (lockfile resolved 18.3.1)
- Vite ^5.1.0 (lockfile resolved 5.4.21)
- TypeScript ^5.3.3
- Tailwind CSS ^3.4.1 (lockfile resolved 3.4.19)
- Framer Motion ^12.29.0
- GSAP ^3.14.2 + @gsap/react
- Zustand ^4.5.0 (lockfile resolved 4.5.7)
- Monaco Editor, React Flow, DnD Kit
- Axios for API transport
- AWS Bedrock runtime client path for direct frontend chat/card generation

### Backend
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0, pydantic-settings 2.1.0
- Neo4j 5.14.1
- ChromaDB 0.4.15
- Redis 5.0.1
- Celery 5.3.4 + RabbitMQ (broker)
- Tree-sitter parsers (Python/JS/TS/Java)
- Bedrock/Nova embedding service path (provider-backed embeddings)

### Infra & deployment clues
- Docker / Docker Compose (see `backend/docker-compose.yml`, `backend/docker-compose.prod.yml`)
- Vercel config (`frontend/vercel.json`)
- Netlify config (`frontend/netlify.toml`)

Version verification sources: `frontend/package.json`, `frontend/package-lock.json`, and `backend/requirements.txt` + compose/runtime config. Items with range vs lock mismatches are flagged in the VALIDATION CHECKLIST.

## Architecture

1) Layered System Architecture

```mermaid
flowchart TB
    subgraph FE[Frontend Layer]
      UI[React UI Pages/Features]
      STORE[Zustand Store]
      CHAT[Amazon Bedrock Nova Client in Browser]
      API_CLIENT[Axios GraphRAG API Client]
    end

    subgraph API[API Layer]
      FASTAPI[FastAPI App src.main]
      ROUTERS[Upload/Query/Projects/Visualization Routers]
      MIDDLEWARE[CORS + Request ID + Error Handlers]
    end

    subgraph BL[Business Logic Layer]
      UPLOAD[UploadService + upload_tasks]
      PARSER[CodeParserService]
      QUERY[QueryService + ContextRetriever]
      VIS[VisualizerAIService deterministic]
      GRAPH[GraphService]
      VECTOR[VectorService]
      ANALYTICS[Client-side Analytics/SRS/Gamification]
    end

    subgraph DATA[Data Layer]
      NEO4J[(Neo4j)]
      CHROMA[(Chroma)]
      REDIS[(Redis Cache)]
      RABBIT[(RabbitMQ)]
      SESSION[(./upload_sessions JSON)]
      LOCAL[(localStorage)]
    end

    UI --> STORE
    UI --> API_CLIENT
    UI --> CHAT
    API_CLIENT --> FASTAPI
    FASTAPI --> ROUTERS
    ROUTERS --> UPLOAD
    ROUTERS --> QUERY
    ROUTERS --> VIS
    UPLOAD --> PARSER
    UPLOAD --> GRAPH
    UPLOAD --> VECTOR
    UPLOAD --> RABBIT
    QUERY --> GRAPH
    QUERY --> VECTOR
    QUERY --> REDIS
    GRAPH --> NEO4J
    VECTOR --> CHROMA
    UPLOAD --> SESSION
    ANALYTICS --> LOCAL
```

Caption: Layered architecture from UI to storage with queue/cache boundaries.

2) Privacy & Trust Layer (detailed)

```mermaid
flowchart LR
    U[User Input: Chat/Code/Uploads] --> V1[Client validation + size limits]
    V1 --> API[FastAPI validation + Pydantic models]
    API --> V2[Request ID + structured errors]
    V2 --> P1[Project processing]
    P1 --> D1[(Neo4j/Chroma/Redis)]
    P1 --> S1[(upload_sessions JSON)]
    API --> E1[Execution policy gate]
    E1 -->|allowed| EXE[Deterministic subprocess trace]
    E1 -->|blocked| ERR[403 sandbox_blocked]
    D1 --> Q[Query/Graph/Context responses]
    Q --> A1[Frontend render]
    A1 --> A2[Local-only analytics aggregates]
    A2 --> ADM[Admin-like trend view in app]
```

Trust controls: request IDs, strict Pydantic payloads, environment-driven execution gate, and local vs server persistence boundaries. There is no built-in consent audit or cryptographic ZKP module — those would be operational extensions.

3) Application Role Flows

```mermaid
flowchart LR
    LAND[Landing] --> HUB[Learning Hub]
    LAND --> APP["/app"]
    LAND --> BUILD["/build"]
    LAND --> DOJO["/dojo"]
    LAND --> VIS["/visualizer"]

    subgraph Learner["Role: Learner User"]
      HUB --> DOJO
      DOJO --> SRS["/srs"]
      SRS --> ANALYTICS["/analytics"]
      ANALYTICS --> ACH["/achievements"]
    end

    subgraph Builder["Role: Builder IDE User"]
      APP --> BUILD
      BUILD --> CHAT[Chat + CodeEditor]
      CHAT --> GRAPH[Graph Panel]
      CHAT --> VIS
    end

    subgraph Maintainer["Role: Project Maintainer Admin-like"]
      UPLOAD[ProjectUpload] --> STATUS[Upload Status Polling]
      STATUS --> PROJECTS["/api/projects"]
      PROJECTS --> DELETE[Delete/Update project data]
    end

    ACH --> EXIT[Exit/Return routes]
    VIS --> EXIT
```

Caption: Learner, Builder, and Maintainer journeys exposed as route surfaces.

4) Data Flow Diagram

```mermaid
flowchart TB
    FE[Frontend: Upload/Chat/Dojo/Visualizer] --> API[FastAPI /api routes]
    API --> VAL[Pydantic validation + limits]
    VAL --> UQ{Request Type}
    UQ -->|Upload| TASK[Celery task or local fallback thread]
    UQ -->|Query| QRY[QueryService + ContextRetriever]
    UQ -->|Visualization Graph| GV[QueryService graph mode]
    UQ -->|Visualization Execution| XV[Visualizer deterministic subprocess]

    TASK --> PARSE[Tree-sitter parser]
    PARSE --> GRAPH[(Neo4j)]
    PARSE --> EMBED[Amazon Bedrock Nova embeddings]
    EMBED --> VDB[(Chroma)]
    QRY --> GRAPH
    QRY --> VDB
    QRY --> CACHE[(Redis)]
    GV --> GRAPH
    XV --> TRACE[Execution trace payload]

    GRAPH --> RESP[JSON responses]
    VDB --> RESP
    TRACE --> RESP
    RESP --> FE
    FE --> LOCAL[(localStorage analytics/SRS/gamification)]
```

Caption: Upload parsing → graph + embeddings → query/visualizer responses. Frontend-only analytics persist locally.

5) AI / ML Pipeline Diagram

```mermaid
flowchart LR
    subgraph OfflineOrBatch[Offline / Batch-like]
      SRC[Uploaded code files] --> PARSE[AST + entity extraction]
      PARSE --> FEAT[Feature text chunks]
      FEAT --> EMB[Amazon Bedrock Nova embedding model]
      EMB --> CH[(Chroma vector index)]
      PARSE --> G[(Neo4j code graph)]
    end

    subgraph Realtime[Realtime]
      PROMPT[User query/chat prompt] --> CTX[Context retrieval]
      CTX --> MERGE[Graph + vector merge]
      MERGE --> OUT[Context answer payload]
      CODE[Visualizer code input] --> DET[Deterministic analyzer]
      DET --> CG[Call graph]
      DET --> XT[Execution trace]
    end

    CH --> CTX
    G --> CTX
```

Caption: Offline embedding/index build and realtime retrieval + deterministic visualizer analysis.

6) Why-this-stack

```mermaid
flowchart LR
    T1[React + Vite] --> C1[Fast interactive SPA + rapid iteration] --> O1[Responsive learning UX]
    T2[Zustand persist] --> C2[Simple global state + local persistence] --> O2[Cross-page continuity]
    T3[FastAPI + Pydantic] --> C3[Typed contracts + auto docs] --> O3[Faster API iteration]
    T4[Neo4j] --> C4[Graph traversals for code relationships] --> O4[Dependency and impact views]
    T5[Chroma + embeddings] --> C5[Semantic code retrieval] --> O5[Context-aware assistance]
    T6[Celery + RabbitMQ] --> C6[Async upload processing] --> O6[Non-blocking ingestion]
    T7[Tree-sitter] --> C7[Deterministic multi-language parsing] --> O7[Reliable entity extraction]
    T8[Deterministic visualizer engine] --> C8[Traceable call/execution analysis] --> O8[Trustworthy step-by-step behavior]
```

Caption: Technology → capability → outcome mapping.

## Quick Start (condensed)

Prerequisites: Python 3.12+, Node.js 18+, Google Cloud project with required APIs.

Backend (dev):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
Copy-Item .env.example .env
# edit .env with keys (GOOGLE_*, DATABASE_URL, etc.)
uvicorn cure_quest.app:app --reload
```

Frontend (dev):

```powershell
cd frontend
npm install
npm run dev
```

Database / seed hints:
- Use AlloyDB or Postgres for full features. For local tests, toggle `DATABASE_URL` to sqlite.
- If using AlloyDB Auth Proxy, run `python scripts/print_alloydb_proxy_command.py` and start the proxy before migrations/seeding.

## Validation Checklist
- [ ] `.env` has `GOOGLE_CLOUD_PROJECT`, model keys, and `DATABASE_URL`.
- [ ] Run `python -m cure_quest.scripts.seed` to seed demo data.
- [ ] `uvicorn cure_quest.app:app --reload` serves `/docs` and `/health`.
- [ ] ADK agent launches from `adk_agents/` and can reach the MCP server.
- [ ] Run `pytest` to validate core backend tests.

## Appendix & Next steps
- Diagrams and long-form design: `docs/` folder.
- Deployment notes: `cloudbuild.yaml`, `cloudbuild.frontend.yaml`, and `cloudrun.env.example`.
- To export mermaid diagrams locally:

```bash
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg
```

If you'd like, I can:
- create a smaller README summary for the GitHub project page,
- add badges (build/test/coverage), or
- split this README into `README.md` + `CONTRIBUTING.md` + `DEPLOY.md`.

---
Updated README to match the requested structure and diagrams.
