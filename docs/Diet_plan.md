# Diet and Recipe Support Agent Integration

Transition the current Diet Support logic from a basic rule-list summary into a comprehensive Recipe Support Agent. This follows the architecture of the `cart-to-kitchen` reference service but adapts it for the Cure-Quest healthcare context.

## User Review Required

> [!IMPORTANT]
> The recipe generation logic will use `gemini-3.1-flash-lite-preview` by default to ensure low-latency responses for meal ideas.
> Images for recipes will be phased: Phase 1 (current) uses static placeholders or curated URLs. Dynamic generation will be added in a follow-up if requested.

## Proposed Changes

### Backend: Models and Data

#### [MODIFY] [models.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/api/models.py)
- Add `RecipeIngredient` (name, quantity, unit).
- Add `DietRecipeSafetyNote` (severity, message, related_to).
- Add `DietRecipe` (id, source, title, description, ingredients, instructions, safety_notes, fit info, image metadata).
- Add `GenerateDietRecipesRequest` and `GenerateDietRecipesResponse`.

#### [NEW] [diet_recipes.json](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/data/diet_recipes.json)
- Create a starter library of 6 curated recipes (e.g., Gentle Oats, Mediterranean Salmon, Turmeric Lentils) to act as Phase 1 content and Phase 2 fallbacks.

---

### Backend: Service Layer

#### [NEW] [recipe_store.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/services/recipe_store.py)
- Implement `RecipeStore` to load `diet_recipes.json`.
- Add utility for deterministic ingredient scaling (measurable vs countable units).
- Add safety annotation rules for common conditions (IBS, Statins, Metformin).

#### [MODIFY] [diet.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/agents/diet.py)
- Integrate `RecipeStore`.
- Add `list_curated_recipes()`.
- Implement `generate_recipes()` using `google-genai` with a strict JSON system instruction.
- Add validation logic to ensure generated recipes don't include blocked ingredients (e.g., grapefruit for statin patients).

#### [MODIFY] [orchestrator.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/agents/orchestrator.py)
- Add `list_diet_recipes()` and `generate_diet_recipes()` to bridge the API and the `DietAgent`.

---

### Backend: API Routes

#### [MODIFY] [routes.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/api/routes.py)
- Add `GET /diet/recipes`.
- Add `POST /diet/recipes/generate`.
- Add `POST /diet/recipes/{recipe_id}/scale`.

---

### Frontend Alignment

#### [MODIFY] [api.ts](file:///c:/Users/shree/project/fronted/frontend/src/lib/api.ts)
- Replace mock logic in `fetchDietRecipes` and `generateDietRecipes` with real `fetch` calls to the new backend endpoints.

## Verification Plan

### Automated Tests
- Test ingredient scaling: Scaling "1.5 lb salmon" for 4 servings (default 2) should yield "3.0 lb salmon".
- Test safety filter: Verify that a request for "Metformin" diet suggestions includes "Take with food" notes and excludes known triggers if IBS is present.
- Test generation fallback: Simulate a model timeout and verify curated recipes are returned instead of an error.

### Manual Verification
1. Open Medication Hub.
2. Select a medication (e.g., Metformin).
3. Verify "Curated Recipes" load immediately.
4. Use the "Recipe Generator" and verify that the results respect the "Available Ingredients" and "Dietary Pattern" inputs.
5. Open a recipe and change servings; verify ingredients scale correctly.
### User Review Required
IMPORTANT

The recipe generation logic will use gemini-3.1-flash-lite-preview by default to ensure low-latency responses for meal ideas. Images for recipes will be phased: Phase 1 (current) uses static placeholders or curated URLs. Dynamic generation will be added in a follow-up if requested.
### answer to this 
I want to have ingredients photos pulled from web like the agent wouldhave and backend would have data so with that u could pull up images from the web i am thinking Wikipedia REST API lets see...
### Tasks
# Task List: Diet and Recipe Support Integration

- [ ] Backend: Models and Data
    - [ ] [models.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/api/models.py): Add recipe models
    - [ ] [diet_recipes.json](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/data/diet_recipes.json): Create curated recipe library
- [ ] Backend: Service Layer
    - [ ] [recipe_store.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/services/recipe_store.py): Create store with scaling and safety logic
    - [ ] [diet.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/agents/diet.py): Integrate store and implement generator
    - [ ] [orchestrator.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/agents/orchestrator.py): Add orchestrator methods
- [ ] Backend: API Routes
    - [ ] [routes.py](file:///c:/Users/shree/project/Cure-Quest/src/cure_quest/api/routes.py): Add diet/recipe endpoints
- [ ] Frontend Alignment
    - [ ] [api.ts](file:///c:/Users/shree/project/fronted/frontend/src/lib/api.ts): Connect to real endpoints
- [ ] Verification
    - [ ] Unit tests for scaling and safety
    - [ ] Manual walkthrough of Medication Hub
