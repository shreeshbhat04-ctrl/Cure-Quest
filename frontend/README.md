
# Cure-Quest Frontend

This Vite app is the polished frontend for Cure-Quest. It follows the `DESIGN.md` sanctuary aesthetic and talks directly to the FastAPI backend.

## Run locally

1. Install dependencies:
   `npm install`
2. Copy the env file:
   `Copy-Item .env.example .env.local`
3. Set:
   - `VITE_API_BASE_URL=http://127.0.0.1:8000`
   - `VITE_DEMO_PATIENT_ID=12`
4. Start the backend from `Cure-Quest`:
   `uvicorn cure_quest.app:app --reload`
5. Start the frontend:
   `npm run dev`

## Current screens

- Dashboard
- Care Maze
- Medication Hub
- History Timeline

All four screens are now driven by the Cure-Quest backend rather than static placeholder content.
