# Plan 3: Information Needed From User

Last reviewed: 2026-04-27

## Purpose

This is the third sequential planning artifact requested in `docs/Final_Project.md`.
Plan 1 audited the current repo. Plan 2 mapped the implementation direction.
This Plan 3 lists the exact information needed from the user before implementation,
and separates urgent answers from details that can wait.

## Quick Priority Summary

To start the first implementation slice, the most important missing information is:

1. Doctor identity details for the supplied Asana user GID.
2. Asana project GID for the Care Approvals project.
3. Whether the app should only open Asana tasks or also mark them complete.
4. The real patient-doctor mapping for patient ID `2`.
5. Confirmation that Phase 1 should be the first build slice.

Everything else can be added in later phases.

## Needed Before Phase 1: Doctor-Aware Asana Tasks

### 1. Doctor Record For Supplied Asana GID

Already known:

- Asana Workspace/Org GID: `1213916290149152`
- Asana Profile/User GID: `1214276322986923`

Needed:

- Doctor full name:Dr surgeon
- Doctor specialty:Gynacologist
- Doctor email address:sreeshhb@gmail.com
- Doctor phone number, if any.
- Whether this doctor should be the default doctor for patient ID `2`: yes for now
- Whether this doctor should appear in the frontend with an existing image asset: yes 
- the other two doctors whould be available but for now i would be interacting with is this 

Why needed:

This lets us seed the first real `doctors` row and map patient ID `2` to a doctor whose Asana tasks route correctly.

### 2. Asana Project GID

Needed:

- The Asana project GID for the Care Approvals project.
:its in .env file

Why needed:

The Asana user GID routes the task to a doctor, but the task also needs the project GID to appear in the correct Care Approvals project.

Where it will go:

- `.env` as `ASANA_PROJECT_GID`
- Or existing deployment secret/config if already configured.

### 3. Asana Task Completion Behavior

Needed decision:

- Should the doctor workspace button only open the Asana task?
- Or should it also have a second button to mark the Asana task complete through the API?

Recommended MVP:

- Use "Open in Asana" first.
- Add "Mark complete" later only if Asana permissions are confirmed.
### ANS: do this 
Why needed:

This decides whether we need `POST /integrations/asana/tasks/{task_gid}/complete` in Phase 1 or can leave it for later.

### 4. Patient-Doctor Mapping For Demo Patient

Current likely demo patient:

- Patient ID: `2`

Needed:

- Which doctor(s) belong to patient ID `2`.
- Which one is default.
- If multiple doctors exist, their names, emails, specialties, and Asana GIDs.

Why needed:

The patient follow-up UI needs two suggested doctor options when possible. If there is only one known doctor, the app can show one mapped doctor plus a custom input option.
### ANS: Only one for now but ai comprehesnsion will be sent to different email,sreeshhb@gmail.com , 1ds23ec200@dsce.edu.in

### 5. Asana Custom Fields

In `Final_Project.md`, the example includes:

- `patient_id_field_gid`
- `urgency_field_gid`

Needed:

- Actual Asana custom field GID for patient ID, if it exists.
- Actual Asana custom field GID for urgency, if it exists.
- Valid urgency enum option GIDs, if urgency is an enum.

Recommended MVP:

- Put patient ID and urgency in task notes first.
- Add custom fields only after GIDs are confirmed.
### Ans: This i will do wait
Why needed:

Asana custom fields fail if the GID or enum option is wrong.

## Needed Before Phase 2: Structured Agent Questions

### 6. Which Actions Need Confirmation

Proposed confirmation-required actions:

- Create Asana doctor handoff.
- Send email.
- Create calendar event.
- Start doctor chat.
- Upload medical document to Drive.

Needed:

- Confirm this list.
- Tell me if any action should execute immediately without confirmation.
### ANS: Like enquiry on what the uploaded documents is like that
Recommended default:

- Require confirmation for Asana, Gmail, and Calendar.
- Upload can execute immediately after user chooses a file.
- Chat can start immediately after user chooses a doctor.

### 7. Preferred Follow-Up UI Style

Plan 2 assumes:

- Two suggested options from the agent.
- One custom text input.

Needed:

- Confirm this UI pattern.
- Tell me whether options should appear inside chat bubbles, modal dialogs, or inline cards under buttons.

Recommended MVP:

- Inline cards inside chat/voice result area.
### ANS:Proceed with that
Why needed:

This affects `ChatAssistant.tsx`, `VoiceAssistant.tsx`, and shared UI components.

### 8. Calendar Scheduling Defaults

Needed:

- Default follow-up timing.
- Default duration.
- Working hours.
- Timezone to use in calendar events.

Known environment timezone:

- Asia/Calcutta

Recommended MVP:
### ANS: ask the user first and then decide
- Default to 45 minutes from now.
- Duration 30 minutes.
- Use Asia/Calcutta for display if the backend needs explicit scheduling text.

### 9. Email Tone And Recipients

Needed:

- Should emails be written as patient-to-doctor, Cure-Quest-to-doctor, or assistant-to-doctor?
- Should the patient be CC'd?
- Should the email include Drive links?
- Should it include Asana task links?

Recommended MVP:
### ANS: proceed with this
- Send as Cure-Quest Assistant on behalf of the patient.
- Include patient summary, recent prescriptions, active conditions, and relevant links.
- Do not CC until explicitly requested.

## Needed Before Phase 3: Profile And History Snapshots

### 10. Patient Profile Fields

Plan 2 proposes:

- Height.
- Weight.
- Blood group.
- Allergies.
- Emergency contact name.
- Emergency contact phone.
- Primary language.
- Notes.

Needed:

- Confirm these fields.
- Add any required fields such as sex, address, insurance, caregiver, or preferred hospital.

Recommended MVP:
### ANS: yes follow this
- Keep medical and care-coordination fields only.
- Avoid insurance/billing fields for now.

### 11. Vitals Fields

Plan 2 proposes:

- Blood pressure.
- Heart rate.
- Blood glucose.
- Temperature.
- Weight.

Needed:

- Confirm which vitals matter for the demo.
- Confirm units.

Recommended MVP:
### ANS: yeh proceed with this
- Blood pressure as text.
- Heart rate as bpm.
- Blood glucose as mg/dL.
- Temperature as Celsius.
- Weight as kg.

### 12. Snapshot Frequency

Needed:

- Should every profile edit create a snapshot?
- Should every upload create a snapshot?
- Should every chat diagnosis create a snapshot only after confirmation?

Recommended MVP:
ANS:Proceed with this
- Profile save creates snapshot.
- Vision upload creates snapshot.
- Doctor handoff creates snapshot.
- Email/calendar/chat only attach to existing snapshot unless they include new clinical content.

## Needed Before Phase 4: Vision Upload And Care Maze

### 13. Upload Categories

Current planned categories:

- Prescription.
- Symptom.
- Other.

Needed:

- Confirm if lab report should be separate from Other.
- Confirm if medication packaging should be separate from Prescription.

Recommended MVP:
ANS:proceed with this
- Keep `PRESCRIPTION`, `SYMPTOM`, and `OTHER`.
- Store detailed document type in metadata when Gemini identifies it.

### 14. Google Drive Folder Naming

Current planned path:

- `CureQuest/{Doctor Name}/{Patient Name}/{Category}/`

Needed:

- Confirm exact folder naming.
- Confirm if doctor name should be "General" when no doctor is selected.
- Confirm if disease name and capture date should be part of filename only or folder path.

Recommended MVP:
### ANS: there are three doctor folders CureQuest/
                                              -Dr Strange
                                              -Dr surgeon
                                              -Dr Shaun
- Folder path: `CureQuest/{Doctor Name}/{Patient Name}/{Category}/`
- Filename: `{disease_name}_{capture_date}.{ext}`

### 15. Care Maze Destinations

Needed:

- Which destination types should the map agent search?
- Pharmacy, clinic, hospital, lab, physiotherapy, dietician, or all?

Recommended MVP:
### ANS:proceed with this
- Pharmacy.
- Clinic.
- Hospital.

### 16. Location Source

Needed:

- Should the app ask browser geolocation permission automatically?
- Or should it only ask after the user clicks "Use my location"?

Recommended MVP:
### ANS: use my locATION
- Ask after the user clicks "Use my location".
- Keep typed location fallback.

## Needed Before Phase 5: Medicine Grounding And Recipe Expansion

### 17. AlloyDB Medicine Schema

Known so far:

- Table mentioned: `indian_medicine`

Needed:

- Exact table names.
- Columns in `indian_medicine`.
- Primary key.
- Which columns contain generic name, brand name, indications, contraindications, food interactions, side effects, substitutes, and dosage.
- Whether vector embeddings already exist for medicine rows.
- If embeddings exist, vector column name and dimensions.
- If grounding should use SQL keyword search, vector search, or both.

Why needed:

The user explicitly said not to make up schema details. Medicine grounding should not be implemented until this is known.
### ANS: Leave it blank for now

### 18. OpenFDA Replacement Scope

Needed decision:

- Should OpenFDA be removed fully?
- Or should it remain as a hidden fallback while the UI says AlloyDB medicine search?

Recommended MVP:
### ANS: yes openFda replaced dont hide it from UI we are goona redirect to wikipedia or something
- Hide OpenFDA from UI.
- Keep the adapter unused for now until AlloyDB replacement is verified.
- Remove it fully after medicine grounding tests pass.

### 19. MedGemma Removal Scope

Needed decision:

- Should MedGemma files/tests/notebooks be deleted?
- Or should runtime code stop using MedGemma while reference notebooks remain untouched?

Recommended MVP:
### ANS: proceed with this
- Remove MedGemma from runtime routes, model routing, frontend copy, and tests.
- Leave notebooks alone unless you explicitly want cleanup.

### 20. Recipe Media Providers

Needed:

- Image provider for ingredients/recipes.
- Tutorial provider for YouTube search.
- Whether API keys are available.

Options:
### ANS: available in .env
- Use official APIs if keys are available.
- Generate safe search links if no keys are available.

Recommended MVP:

- Use generated search links first.
- Add API-backed media later.

### 21. Market Links

Needed:

- Should market links go to Amazon, BigBasket, Zepto, Blinkit, or generic search?
- Should links be direct product links or search result links?

Recommended MVP:
### ANS:Proceed with this
- Use Amazon search links for safe ingredients.
- Do not claim availability or price unless an API is connected.

## Needed Before Phase 6: Doctor-Patient Chat

### 22. Chat Identity

Needed:

- Should doctors log in separately?
- Or is doctor workspace a demo mode switch for now?

Recommended MVP:
### ANS: proceed with this
- Keep the current role switch for demo.
- Use selected doctor ID in frontend state.
- Add real auth later.

### 23. Chat Realtime Method

Needed decision:

- Polling.
- Server-Sent Events.
- WebSocket.

Recommended MVP:
### ANS: yes do this
- Polling every 10 to 20 seconds.

### 24. Chat Safety Rules

Needed:

- Should the assistant ever draft doctor replies?
- Should patient messages be sent directly, or should an agent summarize them first?
- Should emergency terms trigger a warning before sending?

Recommended MVP:
### ANS: Proceed with this but only agent can help rewrite the message if the user wants to use ai in that case the agent would assist with structure and summarize in 50 words his condition
- Store direct patient and doctor messages.
- Let the assistant draft optional summaries, but never send as doctor automatically.
- Emergency terms should show the existing emergency guidance.

## Agent Architecture Decisions Needed

### 25. A2A Communication Map

Plan 2 suggests:

- Root Agent delegates to Vision, Recipe, Communication, Questioner, Data Fetcher, and Map agents.
- Vision delegates to Recipe, Questioner, and Communication.
- Data Fetcher reads AlloyDB medicine and history context.

Needed:

- Confirm this map.
- Tell me if any agent should not talk to another agent.
- Tell me if you want a separate Doctor Agent.

Recommended MVP:
### ANS:proceed
- Add Questioner Agent and Data Fetcher Agent first.
- Add Communication ADK Agent when email/chat wording becomes agent-driven.
- Add Map Agent when Care Maze route endpoint starts.

### 26. Agent Question Behavior

Needed:

- Should the agent always ask before choosing doctor/email/calendar?
- Or can it auto-pick the default doctor and only ask if multiple options exist?

Recommended MVP:
### ANS: proceed
- Ask when creating Asana task, sending email, or creating calendar event.
- Auto-suggest default doctor as option one.

## Credentials And Environment Values Needed

### 27. Required For Integrations

Needed or confirm already configured:

- `ASANA_ACCESS_TOKEN`
- `ASANA_PROJECT_GID`
- `ASANA_WORKSPACE_GID`
- `GOOGLE_API_KEY`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_DRIVE_FOLDER_ID`
- `GOOGLE_MAPS_API_KEY`
- AlloyDB connection values

Do not paste secrets into docs.

Recommended handling:
### ANS: already in .env
- Put secrets in `.env` or deployment secret manager.
- Only paste non-secret IDs, table names, and schema descriptions into planning docs.

## Suggested Answers To Give Me First

To begin Phase 1 cleanly, send this compact block:

```text
Patient ID: 2
Default doctor name:
Default doctor specialty:
Default doctor email:
Default doctor Asana user GID: 1214276322986923
Asana workspace GID: 1213916290149152
Asana Care Approvals project GID:
Doctor workspace task action: open only / open plus complete
Phase 1 approved: yes/no
```

## What I Can Start Without More Information

I can safely start these with reasonable defaults:

- Add doctor and patient-doctor mapping tables.
- Add nullable doctor fields to escalation cases.
- Add frontend types for doctors.
- Add `doctor_id` fields to request models.
- Change "Clear Task" wording to "Open in Asana" once task URLs are available.
- Remove visible MedGemma wording from frontend copy.

I should wait before doing these:

- Final AlloyDB medicine grounding queries.
- Asana custom fields.
- YouTube/Bing/Amazon integrations.
- Deleting MedGemma notebooks.
- Real doctor login/auth.

## Plan 3 Conclusion

The next implementation step should be Phase 1 from Plan 2: doctor routing foundation.
The only truly blocking items are doctor identity, Asana project GID, and whether doctor workspace should open or complete Asana tasks.

Once those are confirmed, the first build can make Asana handoffs route to the selected doctor's workspace and remove the hardcoded doctor task behavior from the frontend.
