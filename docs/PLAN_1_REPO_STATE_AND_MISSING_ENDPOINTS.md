# Plan 1: Repo State And Missing Endpoint Audit

Last reviewed: 2026-04-27

## Purpose

This document is the first sequential planning artifact requested in `docs/Final_Project.md`.
It records the current Cure-Quest repo state and identifies the backend endpoints, schema pieces,
agent wiring, and frontend files that are missing for the final project vision.

This is an audit only. It does not prescribe the exact implementation design yet. That belongs in Plan 2.

## Current Repo Shape

The project currently has these major parts:

- Backend FastAPI route layer: `src/cure_quest/api/routes.py`
- Backend request and response models: `src/cure_quest/api/models.py`
- SQLAlchemy models and lightweight migrations: `src/cure_quest/db/models.py`, `src/cure_quest/db/bootstrap.py`
- Agent layer: `src/cure_quest/agents/*`
- ADK agents: `src/cure_quest/adk/agent.py`, `src/cure_quest/adk/recipe_agent.py`, `src/cure_quest/adk/vision_agent.py`
- External adapters: `src/cure_quest/adapters/*`
- MCP server: `src/cure_quest/mcp/server.py`
- React frontend: `frontend/src/*`
- Existing tests: `tests/*` and `tests/integration/*`

## Existing Backend Endpoints

The current route file exposes these functional groups:

- Auth and Google workspace:
  - `POST /auth/google`
  - `GET /auth/google/status/{patient_id}`
  - `GET /gmail/{patient_id}/health-emails`
  - `POST /gmail/send-care-summary`
- Demo workspace:
  - `GET /demo/patient/{patient_id}/workspace`
- Patient and prescriptions:
  - `POST /patient/intake`
  - `POST /prescription/scan`
  - `POST /patient/check-alternatives`
  - `POST /patient/reminders`
  - `GET /patient/{patient_id}/reminders`
- Escalation and doctor review:
  - `POST /patient/escalate`
  - `POST /patient/notify`
  - `GET /cases/{case_id}`
  - `POST /orchestration/hitl-report`
  - `POST /orchestration/hitl-comprehension`
- Drive and Calendar:
  - `POST /documents/upload`
  - `POST /documents/upload-file`
  - `POST /calendar/events`
- Pharmacy, drug label, diet, and recipes:
  - `POST /drug/label`
  - `POST /pharmacy/search`
  - `POST /orchestration/diet-support`
  - `GET /diet/recipes`
  - `POST /diet/recipes/generate`
  - `POST /diet/recipes/{recipe_id}/scale`
- Conversation and medical routing:
  - `POST /orchestration/conversation-route`
  - `POST /orchestration/voice-route`
  - `POST /orchestration/medical-route`
  - `POST /medical-memory/store`
  - `POST /medical-memory/search`
  - `GET /orchestration/check-in/{patient_id}`
  - `GET /orchestration/routine/{patient_id}`
  - `GET /orchestration/routine-automation/{patient_id}`
  - `GET /orchestration/manifest/{patient_id}`
- Medical model endpoints still present:
  - `POST /medical-models/medgemma`
  - `POST /medical-models/medsiglip/classify`
- Care Maze image endpoints:
  - `POST /caremaze/analyze-symptom`
  - `POST /caremaze/analyze-prescription`

## Key Current Gaps

### 1. Doctor identity and Asana assignment

Current state:

- `src/cure_quest/adapters/ticketing.py` creates Asana tasks with a project GID and optionally a global `settings.asana_assignee_gid`.
- `create_review_ticket()` only accepts `patient_id`, `summary`, and `case_type`.
- The Asana assignee is not selected from a doctor chosen by the patient or mapped in the database.
- `EscalationCase` stores only case and external ticket fields. It does not store `doctor_id`, `doctor_name`, `doctor_email`, or `doctor_asana_gid`.
- There is no `Doctor` table or `patient_doctor_map` table.
- `asana_workspace_gid` exists in settings, but there is no endpoint or script that lists Asana users and stores doctor GIDs.

Missing backend work:

- Add a doctor model or patient-doctor mapping model with:
  - patient id
  - doctor display name
  - doctor specialty
  - doctor email
  - doctor Asana user GID
  - optional default flag
- Add lightweight migrations for the new tables and any new escalation columns.
- Extend `EscalateRequest`, `HitlReportRequest`, and document-flow requests to accept a selected doctor identifier.
- Extend `TicketingAdapter.create_review_ticket()` to accept doctor routing data and always set `assignee` when available.
- Add Asana user discovery support for workspace `1213916290149152`.
- Store user GID `1214276322986923` against the relevant doctor seed data or mapping.
- Return the Asana permalink to the frontend for doctor workspace links.

Missing endpoint candidates:

- `GET /doctors?patient_id={patient_id}` - list doctors available to a patient.
- `POST /doctors` - create or update a doctor record.
- `POST /patients/{patient_id}/doctor-map` - attach a doctor and Asana user GID to a patient.
- `GET /integrations/asana/users?workspace_gid=...` - list Asana users for setup.
- `POST /patient/escalate` should accept `doctor_id` or `doctor_asana_gid`.
- `POST /orchestration/hitl-report` should accept `doctor_id` when `create_case` is true.
- `POST /orchestration/run-document-flow` should accept `doctor_id` for manual review tasks.

Frontend files impacted:

- `frontend/src/lib/api.ts`
- `frontend/src/screens/CareMazeScreen.tsx`
- `frontend/src/screens/HITLScreen.tsx`
- `frontend/src/screens/MedicationHubScreen.tsx`
- `frontend/src/screens/DoctorWorkspaceScreen.tsx`
- `frontend/src/components/ChatAssistant.tsx`
- `frontend/src/components/VoiceAssistant.tsx`

### 2. Doctor workspace task queue is hardcoded

Current state:

- `frontend/src/screens/DoctorWorkspaceScreen.tsx` owns a local hardcoded `tasks` array.
- The "Clear Task" button only removes the local item from React state.
- It does not open Asana, complete a backend task, or sync with the Asana project.
- Patient records and chats in this screen are also hardcoded.

Missing backend work:

- Add a doctor-task listing route that filters by the signed-in doctor or selected doctor GID.
- Decide whether "clear" means:
  - open the Asana task in a new tab, or
  - mark the task complete through Asana, or
  - both through separate buttons.
- Add adapter support for Asana task completion if completion is required.

Missing endpoint candidates:

- `GET /doctor-workspace/{doctor_id}/tasks`
- `GET /doctor-workspace/{doctor_id}/patients`
- `POST /integrations/asana/tasks/{task_gid}/complete`
- `GET /integrations/asana/tasks/{task_gid}` if a task detail panel is needed.

Frontend files impacted:

- `frontend/src/screens/DoctorWorkspaceScreen.tsx`
- `frontend/src/lib/api.ts`

### 3. Patient follow-up question layer is missing

Current state:

- Chat and voice can directly trigger calendar, email, escalation, Drive listing, and prescription lookup based on regex-like intent checks in `Orchestrator._maybe_execute_conversation_tool()`.
- If the user asks to email without an address, the backend returns a text message asking for the address.
- If the user asks to send a doctor handoff, there is no structured question asking which doctor.
- There is no structured UI response such as "Option A", "Option B", and "Custom input".

Missing backend work:

- Add a structured clarification response shape for tool-triggering flows.
- Let agents return proposed options before execution, for example:
  - suggested doctors
  - suggested email recipients
  - suggested calendar slots
  - suggested Asana task summaries
- Add an endpoint to confirm a pending action after the patient chooses an option.

Missing endpoint candidates:

- `POST /orchestration/action-draft`
- `POST /orchestration/action-confirm`
- `GET /patients/{patient_id}/action-options?intent=doctor_handoff`

Frontend files impacted:

- `frontend/src/components/ChatAssistant.tsx`
- `frontend/src/components/VoiceAssistant.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/screens/CareMazeScreen.tsx`
- `frontend/src/screens/MedicationHubScreen.tsx`

### 4. Email sending is not doctor-aware

Current state:

- `POST /gmail/send-care-summary` sends to a raw `to_email` form field.
- Conversation email sending extracts an email address from the message with regex.
- The email builder does not use doctor identity from a doctor mapping table.
- There is no doctor email stored in schema.

Missing backend work:

- Add doctor email to the doctor mapping.
- Let email endpoints accept `doctor_id` as an alternative to raw `to_email`.
- Include selected doctor name and patient context in the care summary.
- Log sent email IDs back onto cases or communication history when relevant.

Missing endpoint candidates:

- `POST /gmail/send-care-summary` should accept `doctor_id`.
- `POST /patient/escalate` should optionally send email to selected doctor.
- `GET /doctors?patient_id={patient_id}` should expose email availability.

Frontend files impacted:

- `frontend/src/lib/api.ts`
- `frontend/src/components/ChatAssistant.tsx`
- `frontend/src/components/VoiceAssistant.tsx`
- `frontend/src/screens/HITLScreen.tsx`
- `frontend/src/screens/CareMazeScreen.tsx`

### 5. Dashboard routine needs shorter accordion summaries

Current state:

- `DashboardScreen.tsx` displays `checkin.message` and up to four routine tasks.
- Routine task notes are rendered directly and can be long.
- Backend routine pulls project tasks from Asana, but does not return a concise summary plus full details separately.

Missing backend work:

- Add fields for concise task summary and full detail.
- Filter Asana tasks by patient and doctor mapping where possible.
- Keep reminders, medication tasks, routine exercise, and calendar events in the routine feed.

Missing endpoint candidates:

- `GET /orchestration/routine/{patient_id}` should return normalized routine item types.
- `GET /calendar/events?patient_id=...` or fold calendar events into routine.

Frontend files impacted:

- `frontend/src/screens/DashboardScreen.tsx`
- `frontend/src/lib/api.ts`

### 6. Patient profile is static and not editable

Current state:

- `frontend/src/screens/Profile.tsx` is static.
- The backend `Patient` model has name, language, date of birth, summary, and Google tokens.
- There are no height, weight, vitals, allergies, emergency contacts, editable profile fields, or prescription history snapshots.

Missing backend work:

- Add profile detail storage, either as columns or a patient profile table.
- Add CRUD endpoints for profile data.
- Include profile data in the workspace payload.

Missing endpoint candidates:

- `GET /patients/{patient_id}/profile`
- `PATCH /patients/{patient_id}/profile`
- `POST /patients/{patient_id}/vitals`
- `GET /patients/{patient_id}/vitals`

Frontend files impacted:

- `frontend/src/screens/Profile.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/hooks/useWorkspace.ts`

### 7. History lacks condition snapshots

Current state:

- `HistoryScreen.tsx` builds a timeline from cases, prescriptions, notifications, and medical memories.
- The `MedicalMemory` table can store metadata, but there is no dedicated patient condition snapshot table.
- The history screen does not show accordion snapshots of patient condition at a point in time.

Missing backend work:

- Add patient condition snapshot storage.
- Capture snapshots when meaningful events occur:
  - profile update
  - prescription upload
  - doctor handoff
  - calendar follow-up
  - email summary sent
  - major chat/agent diagnosis summary
- Add search/query support over snapshots.

Missing endpoint candidates:

- `POST /patients/{patient_id}/condition-snapshots`
- `GET /patients/{patient_id}/condition-snapshots`
- `POST /patients/{patient_id}/history/query`

Frontend files impacted:

- `frontend/src/screens/HistoryScreen.tsx`
- `frontend/src/lib/api.ts`

### 8. Care Maze map is not MCP-driven yet

Current state:

- ADK root agent wires a Google Maps MCP toolset in `src/cure_quest/adk/agent.py`.
- The frontend `CareMazeScreen.tsx` uses an embedded Google Maps iframe based on a typed location.
- The local MCP server does not expose location or map route tools.
- There is no browser geolocation flow.

Missing backend work:

- Add route planning endpoint or agent tool wrapper around MCP map results.
- Add support for user location coordinates.
- Decide whether map routing lives in FastAPI, ADK, MCP server, or a dedicated map agent.

Missing endpoint candidates:

- `POST /caremaze/map-route`
- `POST /caremaze/nearby-care-destinations`
- `POST /orchestration/map-agent`

Frontend files impacted:

- `frontend/src/screens/CareMazeScreen.tsx`
- `frontend/src/lib/api.ts`

### 9. Upload and vision flows are split

Current state:

- `CareMazeScreen.tsx` uploads images to `/caremaze/analyze-symptom`.
- `MedicationHubScreen.tsx` uploads files to `/documents/upload-file`.
- `docs/image_vision_agent.md` describes an auto-classifying Vision Agent.
- `src/cure_quest/adk/vision_agent.py` exists, but the FastAPI upload routes do not expose one unified Vision Agent upload endpoint.

Missing backend work:

- Add a unified upload endpoint that accepts image or document and auto-classifies it.
- Save Drive upload metadata and the analysis result in one workflow.
- Let the workflow delegate to Recipe and Communication agents when needed.

Missing endpoint candidates:

- `POST /vision/upload-analyze`
- `POST /orchestration/vision-flow`

Frontend files impacted:

- `frontend/src/screens/CareMazeScreen.tsx`
- `frontend/src/screens/MedicationHubScreen.tsx`
- `frontend/src/lib/api.ts`

### 10. Medication Hub still references OpenFDA and MedGemma

Current state:

- `MedicationHubScreen.tsx` has a "Fetch openFDA label" action.
- `OpenFDAAdapter` is still wired into `IntegrationAgent`.
- `mcp/server.py` exposes `drug_lookup_label()` through OpenFDA.
- `ModelRoutingService`, `CommunicationsAgent`, `IntegrationAgent`, API models, routes, tests, docs, and frontend copy still reference MedGemma.
- `verify_medgemma_latency.py` and MedGemma notebooks still exist.

Missing backend work:

- Replace the OpenFDA label path with the new search or AlloyDB-grounded medicine source once schema/table names are supplied.
- Remove or disable MedGemma endpoint and request/response models.
- Update model routing so Gemini 3.1 Flash with AlloyDB grounding is the medical reasoning path.
- Keep MedSigLIP only if it is still needed for image classification. If not, strip it too in Plan 2.

Files with likely MedGemma changes:

- `src/cure_quest/config.py`
- `src/cure_quest/api/models.py`
- `src/cure_quest/api/routes.py`
- `src/cure_quest/agents/communications.py`
- `src/cure_quest/agents/integrations.py`
- `src/cure_quest/services/model_routing.py`
- `src/cure_quest/services/huggingface_medical.py`
- `frontend/src/screens/MedicationHubScreen.tsx`
- `tests/test_api_models.py`
- `tests/test_medgemma_proxy.py`
- `verify_medgemma_latency.py`
- `docs/ARCHITECTURE_AND_DESIGN.md`
- `docs/image_vision_agent.md`

### 11. Recipe, market, images, and YouTube support are incomplete

Current state:

- Recipe generation and curated recipe listing already exist.
- Recipe UI currently shows generated recipes and curated fallback library.
- Ingredient and recipe images depend on `image_url` in recipe records or local static assets.
- There are no YouTube search endpoints.
- There are no ingredient market or Amazon redirect endpoints.

Missing backend work:

- Add recipe media enrichment if external search is allowed.
- Add tutorial search provider.
- Add market item model or safe redirect generator.
- Add "recent recipes" storage if the fallback library becomes "recent recipes or try new recipes".

Missing endpoint candidates:

- `GET /diet/recipes/recent?patient_id=...`
- `POST /diet/recipes/{recipe_id}/save`
- `POST /diet/recipes/media-enrich`
- `GET /diet/recipes/{recipe_id}/tutorials`
- `GET /market/ingredients?patient_id=...`

Frontend files impacted:

- `frontend/src/screens/MedicationHubScreen.tsx`
- `frontend/src/lib/api.ts`

### 12. Doctor-patient chat is not live

Current state:

- `DoctorWorkspaceScreen.tsx` has hardcoded chat patients and messages.
- There is no chat message model, endpoint, realtime channel, or patient-side doctor chat screen.

Missing backend work:

- Add chat thread and chat message tables.
- Add endpoints to list threads and send messages.
- Decide whether live updates use polling, Server-Sent Events, WebSockets, or Firebase/Supabase style realtime.

Missing endpoint candidates:

- `GET /chat/threads?patient_id=...`
- `GET /chat/threads?doctor_id=...`
- `GET /chat/threads/{thread_id}/messages`
- `POST /chat/threads/{thread_id}/messages`

Frontend files impacted:

- `frontend/src/screens/DoctorWorkspaceScreen.tsx`
- `frontend/src/components/ChatAssistant.tsx`
- patient-side navigation or a new patient doctor-chat screen
- `frontend/src/lib/api.ts`

## Agent Architecture Gaps

Current state:

- ADK root agent exists and delegates to Recipe Agent and Vision Agent.
- Traditional Python agents exist for communications, routine, HITL, integrations, documents, diet, formulary, intake, temporal memory, and orchestration.
- A2A-style ADK `AgentTool` is present in the Vision Agent for Recipe Agent.

Missing architecture pieces:

- A dedicated Communication ADK agent is not wired.
- A dedicated Questioner or Clarification agent is not wired.
- A dedicated Data Fetcher agent is not wired.
- A2A protocol rules are not documented across all agent pairs.
- The frontend has no structured UI for agent questions and suggested options.

Candidate files to add or modify:

- Add: `src/cure_quest/adk/communication_agent.py`
- Add: `src/cure_quest/adk/questioner_agent.py`
- Add: `src/cure_quest/adk/data_fetcher_agent.py`
- Modify: `src/cure_quest/adk/agent.py`
- Modify: `src/cure_quest/adk/vision_agent.py`
- Modify: `src/cure_quest/agents/orchestrator.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`

## Suggested File Change Map For Future Plans

Backend schema:

- `src/cure_quest/db/models.py`
- `src/cure_quest/db/bootstrap.py`
- Optional seed script: `scripts/seed_shreesha.py`

Backend API:

- `src/cure_quest/api/models.py`
- `src/cure_quest/api/routes.py`

Backend integrations and agents:

- `src/cure_quest/adapters/ticketing.py`
- `src/cure_quest/adapters/gmail.py`
- `src/cure_quest/adapters/calendar.py`
- `src/cure_quest/adapters/medical_memory.py`
- `src/cure_quest/agents/hitl.py`
- `src/cure_quest/agents/orchestrator.py`
- `src/cure_quest/agents/integrations.py`
- `src/cure_quest/agents/communications.py`
- `src/cure_quest/agents/routine.py`
- `src/cure_quest/services/model_routing.py`
- `src/cure_quest/mcp/server.py`

ADK:

- `src/cure_quest/adk/agent.py`
- `src/cure_quest/adk/vision_agent.py`
- New ADK agents as needed.

Frontend:

- `frontend/src/lib/api.ts`
- `frontend/src/hooks/useWorkspace.ts`
- `frontend/src/screens/LoginScreen.tsx`
- `frontend/src/screens/DashboardScreen.tsx`
- `frontend/src/screens/Profile.tsx`
- `frontend/src/screens/DoctorWorkspaceScreen.tsx`
- `frontend/src/screens/CareMazeScreen.tsx`
- `frontend/src/screens/MedicationHubScreen.tsx`
- `frontend/src/screens/HistoryScreen.tsx`
- `frontend/src/screens/HITLScreen.tsx`
- `frontend/src/components/ChatAssistant.tsx`
- `frontend/src/components/VoiceAssistant.tsx`

Tests:

- `tests/test_ticketing.py`
- `tests/test_ticketing_adapter.py`
- `tests/test_api_models.py`
- Add tests for doctor mapping, Asana assignee routing, clarification actions, profile snapshots, and chat.

Docs:

- `docs/Final_Project.md`
- `docs/image_vision_agent.md`
- `docs/ARCHITECTURE_AND_DESIGN.md`
- Add Plan 2 and Plan 3 as separate docs after user approval.

## Highest Priority Missing Endpoints

These should be designed first in Plan 2 because several requested features depend on them:

1. Doctor and patient-doctor mapping endpoints.
2. Doctor-aware Asana escalation endpoint behavior.
3. Structured action draft and confirmation endpoints for "which doctor", "which email", and "when to schedule".
4. Editable patient profile endpoint.
5. Patient condition snapshot endpoints.
6. Unified Vision upload and analysis endpoint.
7. Doctor workspace live task and patient records endpoints.
8. Doctor-patient chat endpoints.

## Notes And Blockers For Later Plans

- The user supplied Asana Workspace/Org GID `1213916290149152`.
- The user supplied Asana Profile/User GID `1214276322986923`.
- The exact AlloyDB schema for medicine grounding is not available yet. Do not invent table structures beyond clearly marked placeholder planning. The user mentioned `indian_medicine` and will provide other tables later.
- The exact doctor list, doctor email addresses, and patient-doctor mapping rules are not yet available.
- The exact A2A communication map between agents is not yet available.
- Git status could not be checked in the sandbox because the repo is marked as dubious ownership for the sandbox user. No destructive action was taken.

## Plan 1 Conclusion

The codebase already has many useful integration pieces: Google OAuth, Drive, Gmail, Calendar, Asana ticket creation, routine pulling, prescription upload, recipe generation, medical memory, and ADK Recipe/Vision agents.

The main missing foundation is identity and confirmation: doctors need first-class records, patients need doctor mappings, tasks and emails must route through selected doctors, and agents must ask structured follow-up questions before executing sensitive actions. Once that foundation is designed, the frontend can replace hardcoded demo flows with live doctor-aware workflows.
