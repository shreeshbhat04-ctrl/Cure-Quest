## Three-Step Plan: Diet Support to Recipe Support in Medication Hub

### Summary
Enhance the current diet agent from rule-only guidance into a recipe support system inside the **Medication Hub**, not Care Maze. Keep the existing `/orchestration/diet-support` behavior for safety summary and backward compatibility, then add a recipe layer with structured recipe data, ingredients, serving scaling, and phased images.

Defaults chosen:
- Primary UI surface: **Medication Hub**
- Recipe pictures: **phased**; v1 uses curated/static or placeholder images, dynamic image fetching/generation is step 3
- Ingredients are **not fetched separately**; they come inside each recipe payload from the backend

### Step 1: Agent Logic and Backend Capability
Current backend is **not good enough** for recipe support yet. The existing `DietAgent` only returns meal rules and a short summary, so it needs a real recipe domain layer.

Planned backend changes:
- Keep `DietAgent.build_diet_support_plan(...)` as the lightweight safety-summary path.
- Add structured recipe models in the API layer:
  - `RecipeIngredient`
  - `DietRecipeSafetyNote`
  - `DietRecipe`
  - `GenerateDietRecipesRequest`
  - `GenerateDietRecipesResponse`
- Add a curated recipe store from JSON:
  - local starter data file with 6-9 recipes
  - each recipe includes title, description, default servings, cook time, ingredients, instructions, condition/medication fit, safety notes, and optional image metadata
- Expand `DietAgent` with:
  - `list_curated_recipes()`
  - `get_recipe(recipe_id)`
  - `scale_recipe(recipe, servings)`
  - `generate_recipes(conditions, medication_name, preferences)`
  - `apply_safety_rules(recipe, conditions, medication_name, avoid_ingredients)`
- Keep safety deterministic first:
  - IBS -> caution on spicy/high-irritation recipes
  - statin-like medication -> grapefruit caution
  - metformin -> “take with food” style meal guidance
  - unknown medication -> general low-risk safety notes only
- Add recipe-specific routes while keeping the old diet route:
  - `GET /diet/recipes`
  - `GET /diet/recipes/{recipe_id}`
  - `POST /diet/recipes/generate`
  - `POST /diet/recipes/{recipe_id}/scale`
- Backend data flow:
  - Medication Hub sends patient id + medication + recipe inputs
  - Orchestrator loads patient conditions
  - Diet agent returns recipes already annotated with ingredients, safety notes, and fit info
- Generation behavior:
  - backend-only, strict JSON contract, max 3 recipes by default
  - fallback to curated recipes if generation fails or returns invalid output
  - short-lived cache by input hash

Important interface decision:
- Keep `/orchestration/diet-support` for the compact diet summary
- Use **new recipe endpoints** for recipe listing/generation so recipe behavior does not overload the legacy route shape

### Step 2: Frontend Plan for Medication Hub
Add the recipe experience inside **MedicationHubScreen** as a first-class section below or beside the medication safety tools, not as a separate page.

Planned Medication Hub structure:
- Keep existing sections:
  - medication selector
  - alternatives
  - label snapshot
  - document upload
- Add a new recipe support area with 4 parts:
  1. **Diet safety summary**
     - show the existing medication-aware meal rules in a compact card
  2. **Recipe generator controls**
     - meal type
     - available ingredients
     - avoid ingredients
     - dietary pattern
     - cuisine preference
     - max cook time
     - servings
  3. **Recipe results**
     - generated recipes first
     - curated recipes below as always-available fallback content
  4. **Recipe detail panel or modal**
     - picture
     - description
     - cook time
     - serving selector
     - scaled ingredients
     - instructions
     - medication/condition safety notes
     - “why this recipe” fit explanation
- Frontend state model:
  - one state for curated recipes
  - one state for generated recipe request status
  - one selected recipe
  - one selected servings count
- Frontend API/types:
  - extend `frontend/src/lib/api.ts` with typed recipe interfaces
  - add `fetchDietRecipes()`
  - add `generateDietRecipes(payload)`
  - optionally add `scaleDietRecipe(recipeId, servings)` if scaling is server-driven
- Preferred scaling behavior:
  - server can expose `/scale`, but for v1 the frontend may scale from structured ingredient quantities if the contract is stable
  - if backend scaling route is used, the UI stays thinner and fully deterministic
- UX constraints:
  - do not remove the current medication tools
  - do not bury recipe support inside a tiny card
  - keep loading, empty, fallback, and error states explicit
  - keep grid/item sizes stable when recipe images load
  - keep warning notes visible without making the page feel alarmist

### Step 3: Fetching of Recipe Pictures and Ingredients
The backend should own all fetching/generation logic; the frontend should only render structured results.

#### Ingredients fetching
- Ingredients come **inside each recipe response**
- No separate ingredient endpoint is needed in v1
- Recipe payload should include:
  - `ingredients: [{ name, quantity, unit }]`
  - `instructions: string[]`
  - `default_servings`
- Scaling flow:
  - frontend sends selected servings
  - backend or frontend computes scaled copy
  - stored recipe source remains unchanged

#### Picture fetching
Use a phased strategy:

**Phase 1**
- curated recipes use static image URLs if available
- otherwise return a placeholder/`image_status: unavailable`
- generated recipe text must render even when no image exists

**Phase 2**
- dynamic image fetching/generation for recipes
- backend fetches or generates picture based on recipe title + description + main ingredients
- cache by recipe-content hash
- return `image_url` preferred; use `image_base64` only if necessary
- enforce timeout so image failure never blocks recipe delivery

Recommended recipe image fields:
- `image_url`
- `image_base64`
- `image_status: "ready" | "pending" | "unavailable"`

Planned fetching behavior:
- frontend requests recipes
- backend returns recipe text immediately
- image field may already be present for curated recipes
- for dynamic images later, backend may return recipe text first and image later on refresh or through a follow-up route if needed

### Test Plan
- Backend unit tests:
  - curated recipe loading
  - missing/invalid recipe file behavior
  - recipe lookup by id
  - scaling rules for countable and measurable units
  - safety rule tagging for IBS/statin/metformin
  - generation fallback on invalid JSON or provider failure
  - blocked avoid-ingredient handling
- API tests:
  - `GET /diet/recipes`
  - `GET /diet/recipes/{id}`
  - `POST /diet/recipes/generate`
  - `POST /diet/recipes/{id}/scale`
- Frontend checks:
  - Medication Hub renders diet summary plus recipe studio
  - generated and curated recipe sections are visually distinct
  - detail panel shows ingredients and instructions
  - servings update ingredient quantities
  - fallback recipes appear when generation fails
  - image placeholders do not break layout
  - existing medication flows still work

### Assumptions
- The current diet summary endpoint remains in place and unchanged for existing callers.
- Medication Hub is the first and primary recipe surface.
- Recipe generation is server-side only.
- v1 includes structured recipes and ingredients, but **dynamic recipe pictures are deferred to step 3**, after the recipe data path is stable.
