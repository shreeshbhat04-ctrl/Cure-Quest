# Plan 2: Implementation Change Map

Last reviewed: 2026-04-27

## Purpose

This is the second sequential planning artifact requested in `docs/Final_Project.md`.
Plan 1 audited the repo. This Plan 2 maps what should change, what should be created,
and how the final Cure-Quest workflows should connect.

This is still a planning document. It should be implemented only after Plan 3 clarifies
the information still needed from the user.

## Guiding Decision

Build the doctor-routing and confirmation layer first.

Reason: Asana assignment, doctor email, doctor workspace tasks, doctor-patient chat,
follow-up questions, and history snapshots all need a reliable way to answer:

- Which patient is acting?
- Which doctor is selected?
- Which action is being drafted?
- Has the patient confirmed the action?
- Where should the result be stored and shown?

## Target Architecture

The target architecture should be:

1. Patient logs in with Google and gets Drive, Calendar, and Gmail access.
2. Patient workspace loads profile, doctors, conditions, prescriptions, reminders, cases,
   messages, snapshots, and routine items.
3. When the patient asks for a sensitive action, the agent drafts a structured action first.
4. The frontend renders two suggested options plus a custom input option.
5. Patient confirms the action.
6. Backend executes the selected action through Gmail, Calendar, Asana, Drive, or chat.
7. The action result is stored in AlloyDB and reflected in dashboard, history, and doctor workspace.

## Implementation Tracks

### Track 1: Doctor Identity And Patient-Doctor Mapping

Goal:

Make doctors first-class records and map each patient to one or more doctors. Store the doctor Asana user GID here, not in frontend state.

Create or modify:

- Modify: `src/cure_quest/db/models.py`
- Modify: `src/cure_quest/db/bootstrap.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `scripts/seed_shreesha.py`

Proposed tables:

`doctors`

- `id`
- `full_name`
- `specialty`
- `email`
- `phone`
- `asana_user_gid`
- `asana_workspace_gid`
- `profile_image_key`
- `created_at`

`patient_doctor_map`

- `id`
- `patient_id`
- `doctor_id`
- `relationship_type`
- `is_default`
- `notes`
- `created_at`

Seed with known Asana details:

- Workspace/Org GID: `1213916290149152`
- Profile/User GID: `1214276322986923`

Keep the actual doctor name/email configurable until the user confirms the real doctor identity.

Add endpoint shapes:

- `GET /doctors?patient_id=2`
- `POST /doctors`
- `PATCH /doctors/{doctor_id}`
- `POST /patients/{patient_id}/doctor-map`
- `PATCH /patients/{patient_id}/doctor-map/{mapping_id}`

Frontend changes:

- Add `DoctorProfile` and `PatientDoctorMap` types in `frontend/src/lib/api.ts`.
- Load doctors in `useWorkspace` or through a separate `fetchDoctors(patientId)` call.
- Replace hardcoded doctor arrays in `HITLScreen.tsx`, `MedicationHubScreen.tsx`, and `DoctorWorkspaceScreen.tsx` with backend doctors.

Acceptance behavior:

- A patient can have multiple doctors.
- One doctor can be marked default.
- Every task/email/calendar handoff can carry `doctor_id`.
- If no doctor is selected, backend returns a structured clarification instead of guessing.

## Track 2: Asana Task Assignment By Doctor GID

Goal:

Every Asana review task should route to the selected doctor by setting `assignee` to that doctor's Asana user GID.

Create or modify:

- Modify: `src/cure_quest/adapters/ticketing.py`
- Modify: `src/cure_quest/agents/hitl.py`
- Modify: `src/cure_quest/agents/orchestrator.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `tests/test_ticketing.py`
- Modify: `tests/test_ticketing_adapter.py`

Change the ticketing adapter contract:

- Current: `create_review_ticket(patient_id, summary, case_type)`
- Target: `create_review_ticket(patient_id, summary, case_type, doctor_asana_gid=None, doctor_name=None, custom_fields=None)`

Task creation behavior:

- Use project GID from `settings.asana_project_gid`.
- Set `assignee` from selected doctor mapping.
- Fall back to `settings.asana_assignee_gid` only when no doctor mapping is available and the action was already confirmed.
- Set due date for doctor review tasks.
- Include patient and doctor context in task notes.
- Return task GID and `permalink_url`.

Add Asana setup support:

- `GET /integrations/asana/users?workspace_gid=1213916290149152`

This endpoint should call the Asana users API and return name/GID pairs. Store the selected GID in `doctors.asana_user_gid`.

Doctor workspace task behavior:

- `GET /doctor-workspace/{doctor_id}/tasks` lists Asana tasks assigned to that doctor.
- "Open Task" opens `permalink_url`.
- "Mark Complete" can be added later via `POST /integrations/asana/tasks/{task_gid}/complete`.
- The current "Clear Task" local state removal should be removed.

Frontend changes:

- `DoctorWorkspaceScreen.tsx` fetches live tasks.
- Task cards show patient, urgency, due date, and Asana link.
- The primary button should open Asana, not delete local state.

Acceptance behavior:

- Creating an escalation with `doctor_id` creates an Asana task assigned to that doctor.
- A doctor can open the Asana task from the doctor workspace.
- The app never "clears" a task only in local React state.

## Track 3: Structured Action Draft And Confirmation

Goal:

Agents should ask the user before executing sensitive actions such as choosing a doctor, sending email, creating Asana tasks, or creating calendar events.

Create or modify:

- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `src/cure_quest/agents/orchestrator.py`
- Add: `src/cure_quest/agents/questioner.py`
- Add optional ADK wrapper: `src/cure_quest/adk/questioner_agent.py`
- Modify: `frontend/src/components/ChatAssistant.tsx`
- Modify: `frontend/src/components/VoiceAssistant.tsx`
- Modify: `frontend/src/lib/api.ts`

Proposed data model:

`pending_actions`

- `id`
- `patient_id`
- `action_type`
- `status`
- `draft_payload_json`
- `options_json`
- `selected_option_json`
- `result_json`
- `created_at`
- `confirmed_at`

Endpoint shapes:

- `POST /orchestration/action-draft`
- `POST /orchestration/action-confirm`
- `GET /patients/{patient_id}/pending-actions`

Draft response shape:

- `action_id`
- `intent`
- `question`
- `options`
- `allow_custom_input`
- `preview`

Option rendering rule:

- Show two best inferred options from the agent.
- Show a custom text input for patient override.

Example doctor handoff draft:

- Question: "Which doctor should receive this review?"
- Option 1: default mapped doctor
- Option 2: next most relevant doctor by specialty
- Custom: patient types a doctor name or email

Example calendar draft:

- Question: "When should I create the follow-up?"
- Option 1: "Today, 45 minutes from now"
- Option 2: "Tomorrow morning"
- Custom: patient types a time

Acceptance behavior:

- Chat no longer silently creates Asana tasks, sends emails, or creates calendar events when a key detail is missing.
- The frontend can render structured choices instead of plain text only.
- Confirmed actions are persisted and visible in history.

## Track 4: Doctor-Aware Email Sending

Goal:

Email sending should use selected doctor data when available, and should store a trace of what was sent.

Create or modify:

- Modify: `src/cure_quest/agents/orchestrator.py`
- Modify: `src/cure_quest/agents/integrations.py`
- Modify: `src/cure_quest/adapters/gmail.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/ChatAssistant.tsx`
- Modify: `frontend/src/components/VoiceAssistant.tsx`

Endpoint changes:

- Extend `POST /gmail/send-care-summary` to accept either:
  - `to_email`, or
  - `doctor_id`

Email behavior:

- Resolve doctor email from `doctors.email`.
- Include doctor name in salutation.
- Include patient summary, active conditions, recent prescriptions, latest snapshot, and request context.
- Store message ID and recipient in `notifications` or `pending_actions.result_json`.

Acceptance behavior:

- If patient says "send this to my doctor", the agent asks which doctor.
- If patient chooses a mapped doctor with email, Gmail sends to that doctor.
- If email is missing, the agent asks for a custom email address.

## Track 5: Patient Profile And Vitals

Goal:

Replace the static profile page with editable patient data and make it usable for history snapshots and doctor review.

Create or modify:

- Modify: `src/cure_quest/db/models.py`
- Modify: `src/cure_quest/db/bootstrap.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `frontend/src/screens/Profile.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/hooks/useWorkspace.ts`

Proposed table:

`patient_profile_details`

- `id`
- `patient_id`
- `height_cm`
- `weight_kg`
- `blood_group`
- `allergies_json`
- `emergency_contact_name`
- `emergency_contact_phone`
- `primary_language`
- `notes`
- `updated_at`

Optional table:

`patient_vitals`

- `id`
- `patient_id`
- `blood_pressure`
- `heart_rate_bpm`
- `blood_glucose_mg_dl`
- `temperature_c`
- `weight_kg`
- `recorded_at`
- `source`

Endpoint shapes:

- `GET /patients/{patient_id}/profile`
- `PATCH /patients/{patient_id}/profile`
- `POST /patients/{patient_id}/vitals`
- `GET /patients/{patient_id}/vitals`

Frontend behavior:

- Profile page shows editable fields for height, weight, blood group, allergies, emergency contact, and notes.
- Recent prescriptions remain linked from workspace data.
- Saving profile creates a condition snapshot.

Acceptance behavior:

- Profile values persist.
- Doctor workspace can read patient profile data.
- History can display patient condition snapshots derived from profile + conditions + prescriptions.

## Track 6: History Snapshots And Queryable Past Diagnosis Context

Goal:

History should store snapshots of patient condition, not only event logs.

Create or modify:

- Modify: `src/cure_quest/db/models.py`
- Modify: `src/cure_quest/db/bootstrap.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `src/cure_quest/agents/orchestrator.py`
- Modify: `src/cure_quest/adapters/medical_memory.py`
- Modify: `frontend/src/screens/HistoryScreen.tsx`
- Modify: `frontend/src/lib/api.ts`

Proposed table:

`patient_condition_snapshots`

- `id`
- `patient_id`
- `snapshot_type`
- `summary`
- `profile_json`
- `conditions_json`
- `prescriptions_json`
- `vitals_json`
- `source_event_type`
- `source_event_id`
- `created_at`

Snapshot triggers:

- Profile update.
- Prescription upload or scan.
- Doctor handoff.
- Email sent.
- Calendar follow-up created.
- Vision analysis completed.
- Chat diagnosis summary confirmed.

Endpoint shapes:

- `POST /patients/{patient_id}/condition-snapshots`
- `GET /patients/{patient_id}/condition-snapshots`
- `POST /patients/{patient_id}/history/query`

Frontend behavior:

- History timeline groups events by type.
- Snapshots render as accordion cards.
- Each snapshot shows "summary first", then expandable profile, conditions, prescriptions, vitals, and linked artifacts.

Acceptance behavior:

- A doctor or patient can inspect what the patient state looked like at the time of a decision.
- Agent history queries can use snapshots as context.

## Track 7: Unified Vision Upload Flow

Goal:

Unify symptom image, prescription image, and other medical document upload through one auto-classifying endpoint.

Create or modify:

- Modify: `src/cure_quest/services/gemini_vision.py`
- Modify: `src/cure_quest/services/image_classifier.py`
- Modify: `src/cure_quest/agents/integrations.py`
- Modify: `src/cure_quest/agents/orchestrator.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `src/cure_quest/adk/vision_agent.py`
- Modify: `frontend/src/screens/CareMazeScreen.tsx`
- Modify: `frontend/src/screens/MedicationHubScreen.tsx`
- Modify: `frontend/src/lib/api.ts`

Endpoint shape:

- `POST /vision/upload-analyze`

Inputs:

- `patient_id`
- `file`
- optional `doctor_id`
- optional `disease_name`
- optional `capture_date`
- optional `create_handoff`

Response:

- classification: `PRESCRIPTION`, `SYMPTOM`, or `OTHER`
- analysis summary
- findings
- severity or medication extraction where applicable
- Drive upload result
- created prescription ID if applicable
- created snapshot ID
- suggested actions

Frontend behavior:

- Care Maze upload area should use the unified endpoint.
- Medication Hub upload should use the same endpoint.
- After upload, show three action buttons below result:
  - "Ask follow-up"
  - "Send doctor handoff"
  - "Chat with doctor"

Acceptance behavior:

- User does not need to label image type manually.
- Upload analysis, Drive save, prescription extraction, and snapshots happen in one workflow.

## Track 8: Care Maze Map Agent

Goal:

Care Maze should use location data and backend map/agent results instead of only embedding a Google Maps iframe.

Create or modify:

- Modify: `src/cure_quest/mcp/server.py`
- Modify: `src/cure_quest/adk/agent.py`
- Add optional ADK agent: `src/cure_quest/adk/map_agent.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `frontend/src/screens/CareMazeScreen.tsx`
- Modify: `frontend/src/lib/api.ts`

Endpoint shapes:

- `POST /caremaze/nearby-care-destinations`
- `POST /caremaze/map-route`

Inputs:

- patient location coordinates or typed location
- destination type: pharmacy, clinic, lab, hospital
- medication or condition context

Frontend behavior:

- Ask browser for location permission.
- Let user type fallback location if denied.
- Show result list plus map link/iframe.
- Route agent response should mention which source was used.

Acceptance behavior:

- Map results can be generated from user location.
- MCP/Maps integration is used through backend/agent flow where possible.

## Track 9: Medication Hub Search, Recipes, Media, And Market

Goal:

Remove OpenFDA-first UX, strip MedGemma mentions, and move medication reasoning toward Gemini 3.1 Flash with AlloyDB grounding.

Create or modify:

- Modify: `src/cure_quest/config.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `src/cure_quest/agents/communications.py`
- Modify: `src/cure_quest/agents/documents.py`
- Modify: `src/cure_quest/agents/integrations.py`
- Modify: `src/cure_quest/services/model_routing.py`
- Modify or retire: `src/cure_quest/services/huggingface_medical.py`
- Modify or retire: `src/cure_quest/adapters/openfda.py`
- Modify: `src/cure_quest/mcp/server.py`
- Modify: `frontend/src/screens/MedicationHubScreen.tsx`
- Modify: `frontend/src/screens/AboutScreen.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `docs/ARCHITECTURE_AND_DESIGN.md`
- Modify: `docs/image_vision_agent.md`
- Modify tests that reference MedGemma or OpenFDA.

Model routing target:

- General conversation: Gemini 3.1 Flash.
- Medical text reasoning: Gemini 3.1 Flash with AlloyDB grounding.
- Medical image reasoning: Gemini Vision / Gemini 3.1 Flash multimodal path.
- Medicine lookup: AlloyDB-grounded search once the user supplies table details.

Known table placeholder:

- `indian_medicine`

Do not invent the final medicine schema until Plan 3 information is answered.

Endpoint direction:

- Replace `POST /drug/label` with `POST /medicine/search` or `POST /medicine/grounded-answer`.
- Keep `POST /drug/label` temporarily as a compatibility wrapper only if needed by frontend migration.

Recipe UI changes:

- First show "what to take" and "what not to take" from prescription/medication context.
- Then ask the recipe agent to create recipes.
- Render generated recipes after the agent response.
- Pre-fill ingredients and quantities from agent output.
- Add recent recipes.
- Add recipe tutorial results.
- Add safe ingredient market links.

Endpoint shapes:

- `POST /medicine/grounded-answer`
- `GET /diet/recipes/recent?patient_id=2`
- `POST /diet/recipes/{recipe_id}/save`
- `GET /diet/recipes/{recipe_id}/tutorials`
- `GET /market/ingredients?patient_id=2&recipe_id=...`

Acceptance behavior:

- No visible MedGemma wording remains in the frontend.
- OpenFDA is no longer the primary medication lookup feature.
- Gemini 3.1 Flash plus AlloyDB grounding becomes the stated model path.

## Track 10: Doctor-Patient Chat

Goal:

Create a real chat workflow between patient and doctor.

Create or modify:

- Modify: `src/cure_quest/db/models.py`
- Modify: `src/cure_quest/db/bootstrap.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `src/cure_quest/api/routes.py`
- Modify: `frontend/src/screens/DoctorWorkspaceScreen.tsx`
- Modify: `frontend/src/components/ChatAssistant.tsx`
- Add patient-side doctor chat view if existing navigation cannot hold it.
- Modify: `frontend/src/lib/api.ts`

Proposed tables:

`chat_threads`

- `id`
- `patient_id`
- `doctor_id`
- `subject`
- `status`
- `created_at`
- `updated_at`

`chat_messages`

- `id`
- `thread_id`
- `sender_role`
- `sender_display_name`
- `body`
- `created_at`

Endpoint shapes:

- `GET /chat/threads?patient_id=2`
- `GET /chat/threads?doctor_id=1`
- `POST /chat/threads`
- `GET /chat/threads/{thread_id}/messages`
- `POST /chat/threads/{thread_id}/messages`

Realtime decision:

- Start with polling every 10 to 20 seconds for MVP.
- Upgrade later to WebSocket or Server-Sent Events if needed.

Acceptance behavior:

- Doctor workspace chat is not hardcoded.
- Patient can start or continue a thread with a selected doctor.
- Chat history persists.

## Track 11: Dashboard Routine Accordion

Goal:

Make the dashboard routine concise but expandable.

Create or modify:

- Modify: `src/cure_quest/adapters/ticketing.py`
- Modify: `src/cure_quest/agents/routine.py`
- Modify: `src/cure_quest/agents/orchestrator.py`
- Modify: `src/cure_quest/api/models.py`
- Modify: `frontend/src/screens/DashboardScreen.tsx`
- Modify: `frontend/src/lib/api.ts`

Routine item response target:

- `id`
- `source`: Asana, Calendar, Medication, Exercise, Reminder
- `title`
- `short_summary`
- `full_details`
- `due_at`
- `completed`
- `assignee_name`
- `permalink_url`

Frontend behavior:

- Show compact cards by default.
- Expand each card to view full details.
- Asana-backed tasks link out to Asana.
- Calendar-backed items link out to Calendar.

Acceptance behavior:

- Dashboard is scannable.
- Full details remain available without cluttering the first view.

## Track 12: ADK Agent Architecture And A2A Rules

Goal:

Make agent delegation explicit and consistent.

Create or modify:

- Add: `src/cure_quest/adk/communication_agent.py`
- Add: `src/cure_quest/adk/questioner_agent.py`
- Add: `src/cure_quest/adk/data_fetcher_agent.py`
- Add optional: `src/cure_quest/adk/map_agent.py`
- Modify: `src/cure_quest/adk/agent.py`
- Modify: `src/cure_quest/adk/vision_agent.py`
- Modify: `src/cure_quest/adk/recipe_agent.py`
- Modify: `docs/ARCHITECTURE_AND_DESIGN.md`

Suggested A2A map:

- Root Agent delegates:
  - Vision Agent for uploads and images.
  - Recipe Agent for diet-safe recipe generation.
  - Communication Agent for email/chat/calendar wording.
  - Questioner Agent for missing user decisions.
  - Data Fetcher Agent for AlloyDB grounded lookup.
  - Map Agent for Care Maze location work.
- Vision Agent delegates:
  - Recipe Agent when medication/diet is relevant.
  - Questioner Agent if doctor/action confirmation is needed.
  - Communication Agent for patient-friendly summary.
- Data Fetcher Agent provides:
  - medicine facts from AlloyDB
  - patient profile snapshots
  - historical condition context

Open item:

- The exact agent-to-agent communication map should be confirmed by the user in Plan 3.

## Implementation Order

### Phase 1: Doctor routing foundation

1. Add doctor and patient-doctor mapping tables.
2. Seed the supplied Asana workspace/user GID.
3. Add doctor list and mapping endpoints.
4. Update workspace payload or frontend API to load doctors.
5. Update Asana ticket creation to accept selected doctor GID.
6. Update patient escalation paths to carry `doctor_id`.
7. Update doctor workspace tasks to open Asana instead of clearing local state.

Why first:

This unlocks the most urgent user request: tasks route into the correct doctor's Asana workspace.

### Phase 2: Structured confirmation layer

1. Add pending action models.
2. Add action draft and confirm endpoints.
3. Add frontend option UI for chat and voice.
4. Route doctor handoff, email, and calendar creation through draft/confirm.

Why second:

This prevents accidental emails, calendar events, and Asana tasks.

### Phase 3: Profile and history

1. Add editable profile and vitals.
2. Add condition snapshots.
3. Capture snapshots from important workflows.
4. Render snapshots as accordions in History.
5. Use snapshots in doctor workspace patient records.

Why third:

This gives doctors better context and gives agents past-condition state to query.

### Phase 4: Unified upload and Care Maze

1. Create unified vision upload endpoint.
2. Move Care Maze and Medication Hub uploads onto it.
3. Add post-upload action buttons.
4. Add map route/location endpoints.
5. Connect location permission in frontend.

Why fourth:

This consolidates split upload behavior and makes Care Maze feel like one workflow.

### Phase 5: Medication Hub model and search cleanup

1. Remove MedGemma endpoint and frontend mentions.
2. Replace model routing with Gemini 3.1 Flash plus AlloyDB grounding.
3. Replace OpenFDA-first label lookup with medicine grounded search.
4. Rework recipe UI to start from "take / do not take".
5. Add recent recipes, tutorials, media enrichment, and market links.

Why fifth:

This depends on the AlloyDB medicine schema the user will provide later.

### Phase 6: Doctor-patient chat

1. Add chat tables.
2. Add chat endpoints.
3. Replace hardcoded doctor workspace chat.
4. Add or wire patient-side doctor chat.
5. Start with polling.

Why sixth:

It is important but can be built cleanly once doctor identity exists.

## Test Plan Direction

Add or update tests around:

- Doctor model serialization.
- Patient-doctor mapping CRUD.
- Asana task creation includes `assignee`.
- Escalation with `doctor_id` stores doctor context on case.
- Action draft returns options and does not execute.
- Action confirm executes and stores result.
- Gmail send resolves `doctor_id` to doctor email.
- Profile update persists and creates snapshot.
- History snapshot list returns accordion-ready data.
- Unified vision upload returns classification, analysis, and Drive result.
- Doctor workspace tasks are fetched from backend.
- MedGemma routes and frontend references are removed.

## Main Risks

- AlloyDB schema is not fully known yet, so medicine grounding should wait for Plan 3 answers.
- Doctor email and doctor identity are not fully known yet.
- Completing Asana tasks through API may need extra permissions.
- Browser geolocation needs graceful fallback.
- YouTube, Bing image search, and Amazon redirects may need API keys, scraping policy decisions, or safer search-link fallback.
- Removing MedGemma should be done carefully so tests and docs do not point to missing models.

## Plan 2 Conclusion

The practical path is not to implement every feature at once. The first real build slice should be:

1. Doctor records and patient-doctor mapping.
2. Asana assignment using selected doctor GID.
3. Structured confirmation UI and backend action drafts.
4. Doctor-aware email and calendar execution.

After that, profile snapshots, unified upload, medication grounding, and live chat can attach to the same foundation instead of becoming separate demo flows.
