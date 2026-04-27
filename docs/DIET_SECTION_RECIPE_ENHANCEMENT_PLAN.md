# Diet Section Recipe Enhancement Plan

This document describes how to evolve the current diet section from a short medication-aware rule list into a full recipe experience. It extracts the useful recipe-generation patterns from the reference implementation while intentionally excluding non-recipe commerce behavior.

The plan also avoids copying names, branding, demo users, or identity labels from the reference material. Treat the reference as an architectural pattern source, not as copy, product language, or identity material.

## 1. Current State

The current diet flow is lightweight and lives across:

- `src/cure_quest/agents/diet.py`
- `src/cure_quest/agents/orchestrator.py`
- `src/cure_quest/api/models.py`
- `src/cure_quest/api/routes.py`
- `frontend/src/lib/api.ts`
- `frontend/src/screens/CareMazeScreen.tsx`

Today the backend accepts a patient id, an optional medication name, and an optional location query. It returns:

- relevant conditions
- a `diet_plan` object
- medication-aware meal rules
- a short plan summary
- pharmacy search results

The frontend renders the diet output as a card with the plan summary and a list of meal rules. This is useful for safety reminders, but it does not yet help the patient choose meals, inspect ingredients, scale servings, or generate condition-aware recipes.

## 2. Target Experience

The enhanced diet section should become a "recipe support" surface inside the existing care flow.

Primary user actions:

1. Review safe meal guidance for the selected medication and known conditions.
2. Browse a small set of curated recipes that are always available.
3. Generate new recipes from condition, medication, preferences, meal type, and optional available ingredients.
4. Open a recipe detail view with ingredients, servings, cook time, instructions, and safety notes.
5. Scale ingredients by serving count without changing the underlying recipe record.
6. Understand why a recipe is suggested, including medication and condition fit.
7. See graceful fallback content when generation or image creation is unavailable.

The recipe experience should remain recipe-only. It should focus on meal guidance, recipe generation, recipe detail, serving scaling, and safety notes. It should not bring over non-recipe commerce workflows, inventory assumptions, or reference-specific names, screenshots, or user-facing copy.

## 3. Reference Patterns To Keep

The reference implementation has several useful recipe-only patterns:

1. Structured recipe schema
   Use a stable object shape with recipe id, title, description, default servings, cook time, ingredients, instructions, and optional image data.

2. Recipe list and recipe detail separation
   Keep a list view for browse/generate results and a detail view for instructions and scaled ingredients.

3. JSON-backed curated recipes for phase one
   Start with a simple local recipe data file before introducing persistent recipe tables.

4. Ingredient scaling
   Store ingredient quantity and unit separately so the UI can scale from default servings to 2, 4, 6, 8, or 10 servings.

5. Generation contract
   Ask the model to return strict JSON, limit the number of recipes, include detailed steps, and require quantities for each ingredient.

6. Fallback behavior
   If model generation fails, return deterministic fallback recipes rather than leaving the diet section empty.

7. Caching
   Cache generated recipes by a hash of the generation inputs. Use a short TTL so repeated requests feel fast while avoiding stale personal context for too long.

8. Progressive images
   Recipe text should render first. Images should be optional, cached, compressed, and never block the main response.

9. Loading, empty, error, and success states
   The UI should make generation progress visible and should explain what the user can do when there is not enough input.

## 4. Reference Patterns To Exclude

Do not port these parts:

- commerce-specific service boundaries
- inventory or item-availability logic
- order lifecycle behavior
- commerce assistant copy
- real-time events tied to commerce state
- reference-specific brand or user names

For this app, recipe generation should be driven by health context and user-entered food preferences rather than by commerce state.

## 5. Product Requirements

### 5.1 Core Requirements

The diet section should support:

- medication-aware recipe safety notes
- condition-aware recipe filtering and warnings
- curated starter recipes
- generated recipe suggestions
- recipe detail inspection
- serving-size scaling
- ingredient quantities and units
- step-by-step instructions
- loading, empty, error, and fallback states
- typed API contracts between frontend and backend
- deterministic tests for parsing, scaling, fallback, and safety flags

### 5.2 Safety Requirements

Recipe guidance must stay bounded:

- Do not claim a recipe treats, cures, or prevents disease.
- Do not override clinician instructions.
- Do not recommend ingredients known to conflict with the active medication rules already modeled in the app.
- When safety is uncertain, mark the recipe with a caution flag instead of presenting it as safe.
- Always include a short patient-facing safety note when medication or condition context affects a recipe.
- Keep a clear path to human review for high-risk diet or medication questions.

### 5.3 Personalization Inputs

The generator should use:

- patient id
- known chronic conditions
- selected medication name
- recent prescription context when available
- meal type, such as breakfast, lunch, dinner, snack, or any
- available ingredients typed by the user
- avoid list typed by the user
- cuisine preference, optional
- cooking time preference, optional
- serving count
- dietary pattern, optional, such as vegetarian, high-fiber, low-spice, or gentle meal

### 5.4 Output Expectations

Each generated recipe should include:

- `recipe_id`
- `source`, either `curated`, `generated`, or `fallback`
- `title`
- `description`
- `default_servings`
- `cook_time`
- `meal_type`
- `ingredients`
- `instructions`
- `safety_notes`
- `condition_fit`
- `medication_fit`
- `avoid_flags`
- `image_url` or `image_base64`, optional
- `generation_trace`, optional internal metadata

## 6. Proposed Backend Design

### 6.1 New Domain Models

Add typed Pydantic models in `src/cure_quest/api/models.py`.

```python
class RecipeIngredient(BaseModel):
    name: str
    quantity: float
    unit: str


class DietRecipeSafetyNote(BaseModel):
    severity: str
    message: str
    related_to: str | None = None


class DietRecipe(BaseModel):
    recipe_id: str
    source: str
    title: str
    description: str
    default_servings: int
    cook_time: str
    meal_type: str | None = None
    ingredients: list[RecipeIngredient]
    instructions: list[str]
    safety_notes: list[DietRecipeSafetyNote] = Field(default_factory=list)
    condition_fit: list[str] = Field(default_factory=list)
    medication_fit: list[str] = Field(default_factory=list)
    avoid_flags: list[str] = Field(default_factory=list)
    image_url: str | None = None
    image_base64: str | None = None


class GenerateDietRecipesRequest(BaseModel):
    patient_id: int
    medication_name: str | None = None
    meal_type: str = "any"
    available_ingredients: list[str] = Field(default_factory=list)
    avoid_ingredients: list[str] = Field(default_factory=list)
    cuisine_preference: str | None = None
    dietary_pattern: str | None = None
    max_cook_minutes: int | None = None
    servings: int = 4
    count: int = 3


class GenerateDietRecipesResponse(BaseModel):
    patient_id: int
    conditions: list[dict]
    medication_name: str | None = None
    recipes: list[DietRecipe]
    fallback_used: bool = False
    safety_summary: str
```

### 6.2 New Backend Data File

Create:

- `src/cure_quest/data/diet_recipes.json`

Use this file for phase-one curated recipes. Keep entries generic and health-context aware.

Example structure:

```json
{
  "recipes": [
    {
      "recipe_id": "gentle_oats_bowl",
      "source": "curated",
      "title": "Gentle Oats Bowl",
      "description": "A simple, steady breakfast built around oats, fruit, and mild toppings.",
      "default_servings": 2,
      "cook_time": "12 minutes",
      "meal_type": "breakfast",
      "ingredients": [
        { "name": "Rolled oats", "quantity": 1, "unit": "cup" },
        { "name": "Milk or fortified milk alternative", "quantity": 2, "unit": "cups" },
        { "name": "Banana", "quantity": 1, "unit": "piece" }
      ],
      "instructions": [
        "Warm the oats and milk together over medium heat until soft.",
        "Stir regularly until the mixture thickens.",
        "Top with sliced banana and serve warm."
      ],
      "condition_fit": ["gentle meal"],
      "medication_fit": [],
      "avoid_flags": [],
      "safety_notes": []
    }
  ]
}
```

The starter file should include 6 to 9 recipes across breakfast, lunch, dinner, and snacks. The recipes should avoid strong medical claims and should be easy to modify later.

### 6.3 New Service Layer

Expand `DietAgent` in `src/cure_quest/agents/diet.py` instead of scattering recipe logic across routes.

Recommended new methods:

```python
class DietAgent:
    def list_curated_recipes(self) -> list[dict]:
        ...

    def get_recipe(self, recipe_id: str) -> dict | None:
        ...

    def scale_recipe(self, recipe: dict, servings: int) -> dict:
        ...

    def generate_recipes(
        self,
        conditions: list[BrainCondition],
        medication_name: str | None,
        preferences: dict,
    ) -> dict:
        ...

    def apply_safety_rules(
        self,
        recipe: dict,
        conditions: list[BrainCondition],
        medication_name: str | None,
        avoid_ingredients: list[str],
    ) -> dict:
        ...
```

Keep parsing, validation, scaling, and safety annotation close to this agent. The route should only validate the request and delegate.

### 6.4 Recipe Store Helper

Add a small helper module:

- `src/cure_quest/services/recipe_store.py`

Responsibilities:

- load JSON recipes
- validate recipe shape
- return all curated recipes
- return one recipe by id
- scale ingredients
- normalize ingredient names
- avoid crashing when the JSON file is missing or invalid

This mirrors the useful reference pattern but fits the current FastAPI/Pydantic codebase instead of adding a separate gRPC service.

### 6.5 Generation Service

Add a generation helper only after the curated recipe path is stable:

- `src/cure_quest/services/recipe_generation.py`

Responsibilities:

- build a strict recipe generation prompt
- call the configured model or ADK agent
- parse strict JSON
- validate generated recipes
- cap output to 3 recipes by default
- apply safety annotations after generation
- return fallback recipes on timeout, invalid JSON, or provider errors
- cache successful generations by input hash

Do not call external model APIs directly from the frontend. All generation should happen on the backend so patient context and safety rules stay server-side.

### 6.6 Prompt Contract

The prompt should enforce a strict schema and safety boundaries.

Required model behavior:

- Return only JSON.
- Return an array of recipe objects.
- Generate at most the requested count.
- Include 5 to 8 clear instruction steps.
- Include quantities and units for every ingredient.
- Use available ingredients when provided, but do not invent unsafe ingredients.
- Respect avoid ingredients.
- Do not include medication advice beyond food-safety notes.
- Do not claim disease treatment.
- If unsure about a conflict, include a caution note.

Suggested prompt shape:

```text
Generate {count} practical recipes for a patient-facing diet support screen.

Context:
- Conditions: {condition_names}
- Medication focus: {medication_name_or_none}
- Meal type: {meal_type}
- Available ingredients: {available_ingredients}
- Avoid ingredients: {avoid_ingredients}
- Dietary pattern: {dietary_pattern}
- Cuisine preference: {cuisine_preference}
- Maximum cooking time: {max_cook_minutes}
- Servings: {servings}

Rules:
- Return only valid JSON.
- Use this schema exactly.
- Do not claim the recipe treats or cures a condition.
- Include a safety note if medication or condition context affects the recipe.
- Avoid ingredients listed in the avoid list.
- Prefer simple, low-risk recipes when medical context is limited.

Schema:
[
  {
    "title": "string",
    "description": "string",
    "default_servings": 4,
    "cook_time": "string",
    "meal_type": "string",
    "ingredients": [
      { "name": "string", "quantity": 1.0, "unit": "string" }
    ],
    "instructions": ["string"],
    "safety_notes": [
      { "severity": "info|caution", "message": "string", "related_to": "string|null" }
    ],
    "condition_fit": ["string"],
    "medication_fit": ["string"],
    "avoid_flags": ["string"]
  }
]
```

### 6.7 Safety Rule Layer

Start with deterministic rules already implied by the current diet agent:

- IBS: mark spicy, high-irritation, or known trigger-heavy recipes with caution.
- Statin medication names: flag grapefruit and grapefruit juice.
- Metformin medication names: prefer meals that can be eaten with medication and avoid meal-skipping language.
- Unknown medication: use general food guidance and avoid claiming interaction safety.

Add a simple rule table:

```python
MEDICATION_FOOD_RULES = {
    "statin": {
        "avoid": ["grapefruit", "grapefruit juice"],
        "note": "Avoid grapefruit while this medication is active unless the clinician says otherwise.",
    },
    "metformin": {
        "prefer": ["meal", "snack"],
        "note": "Taking this medication with food can reduce stomach irritation for many patients.",
    },
}
```

This can later be upgraded to use OpenFDA label context or a curated interaction dataset.

### 6.8 API Routes

Add recipe-specific routes. Keep the existing `/orchestration/diet-support` endpoint backward compatible.

Recommended routes:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/diet/recipes` | Return curated recipe list |
| `GET` | `/diet/recipes/{recipe_id}` | Return one curated recipe |
| `POST` | `/diet/recipes/generate` | Generate condition-aware recipe suggestions |
| `POST` | `/diet/recipes/{recipe_id}/scale` | Return a scaled copy of a recipe |

Optional later route:

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/diet/recipes/{recipe_id}/image` | Generate or refresh a recipe image |

### 6.9 Orchestrator Updates

Add a method to `Orchestrator`:

```python
def generate_diet_recipes(self, payload: GenerateDietRecipesRequest) -> dict:
    conditions = self.temporal_memory.get_relevant_conditions(payload.patient_id)
    return self.diet.generate_recipes(
        conditions=conditions,
        medication_name=payload.medication_name,
        preferences=payload.model_dump(),
    )
```

The Orchestrator remains responsible for patient context retrieval. The DietAgent remains responsible for recipe rules and generation behavior.

## 7. Proposed Frontend Design

### 7.1 Current Screen Placement

The diet enhancement can live inside `frontend/src/screens/CareMazeScreen.tsx` at first because that screen already owns the diet support route and medication focus input.

Once the feature grows, split it into components:

- `frontend/src/components/diet/DietRecipeStudio.tsx`
- `frontend/src/components/diet/RecipeGeneratorPanel.tsx`
- `frontend/src/components/diet/RecipeGrid.tsx`
- `frontend/src/components/diet/RecipeCard.tsx`
- `frontend/src/components/diet/RecipeDetailPanel.tsx`
- `frontend/src/components/diet/ServingsSelector.tsx`
- `frontend/src/components/diet/SafetyNotes.tsx`

### 7.2 UI Sections

Recommended sections:

1. Diet guidance summary
   Keep the existing medication-aware summary and rules, but make them a compact safety context above the recipe tools.

2. Recipe generator controls
   Inputs:
   - meal type
   - available ingredients
   - avoid ingredients
   - dietary pattern
   - maximum cook time
   - servings

3. Generated recipes
   A responsive recipe grid with image, title, description, cook time, servings, and safety chips.

4. Curated recipes
   Always available fallback recipes, visually distinct from generated results.

5. Recipe detail panel
   A side panel or modal showing:
   - image
   - title
   - cook time
   - serving selector
   - scaled ingredients
   - instructions
   - medication and condition notes

### 7.3 State Model

Use local state unless the recipe experience becomes cross-screen.

```ts
type RecipeViewState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; recipes: DietRecipe[]; fallbackUsed: boolean }
  | { status: 'error'; message: string };
```

Keep generated recipes separate from curated recipes:

```ts
const [curatedRecipes, setCuratedRecipes] = useState<DietRecipe[]>([]);
const [generatedState, setGeneratedState] = useState<RecipeViewState>({ status: 'idle' });
const [selectedRecipe, setSelectedRecipe] = useState<DietRecipe | null>(null);
```

### 7.4 Frontend API Types

Extend `frontend/src/lib/api.ts`:

```ts
export interface RecipeIngredient {
  name: string;
  quantity: number;
  unit: string;
}

export interface DietRecipeSafetyNote {
  severity: 'info' | 'caution';
  message: string;
  related_to: string | null;
}

export interface DietRecipe {
  recipe_id: string;
  source: 'curated' | 'generated' | 'fallback';
  title: string;
  description: string;
  default_servings: number;
  cook_time: string;
  meal_type: string | null;
  ingredients: RecipeIngredient[];
  instructions: string[];
  safety_notes: DietRecipeSafetyNote[];
  condition_fit: string[];
  medication_fit: string[];
  avoid_flags: string[];
  image_url: string | null;
  image_base64: string | null;
}

export interface GenerateDietRecipesPayload {
  patient_id: number;
  medication_name?: string | null;
  meal_type: string;
  available_ingredients: string[];
  avoid_ingredients: string[];
  cuisine_preference?: string | null;
  dietary_pattern?: string | null;
  max_cook_minutes?: number | null;
  servings: number;
  count: number;
}
```

Add functions:

```ts
export async function fetchDietRecipes() {
  return request<{ recipes: DietRecipe[] }>('/diet/recipes');
}

export async function generateDietRecipes(payload: GenerateDietRecipesPayload) {
  return request<GenerateDietRecipesResponse>('/diet/recipes/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
```

### 7.5 Layout Guidance

Follow the existing React and Tailwind stack.

Implementation details:

- Use semantic buttons for recipe selection.
- Avoid making the recipe area look like an embedded preview.
- Keep the recipe grid stable across loading and success states.
- Use accessible labels on inputs and serving selectors.
- Do not rely on color alone for caution notes.
- Keep card content from changing layout height dramatically when images load.
- Render skeleton or soft loading placeholders while generation is running.
- Keep empty states actionable, for example asking for a meal type or a few available ingredients.
- Keep generated images optional and provide a stable fallback visual.

## 8. Image Strategy

Images are useful for the recipe section, but text should be the primary response.

Phase-one image strategy:

- Use static local images for curated recipes if available.
- Use a neutral placeholder for recipes without an image.
- Do not block recipe generation on image generation.

Phase-two image strategy:

- Add optional backend image generation.
- Cache image results by recipe title, description, and main ingredients.
- Compress generated images before returning to the frontend.
- Prefer `image_url` for static or stored images.
- Use `image_base64` only for small generated images or short-term transport.
- Set a timeout and return the recipe without an image if image generation fails.

Suggested image metadata fields:

```python
image_url: str | None
image_base64: str | None
image_status: Literal["ready", "pending", "unavailable"]
```

## 9. Data Validation And Parsing

Generated recipe data should be treated as untrusted input.

Validation rules:

- `title` must be non-empty and under a reasonable length.
- `description` must be non-empty.
- `default_servings` must be between 1 and 12.
- `ingredients` must contain 3 to 12 items.
- every ingredient must have `name`, `quantity`, and `unit`.
- `instructions` must contain 3 to 10 steps.
- every safety note must have a known severity.
- generated recipes must not include avoided ingredients.
- generated recipes must not include blocked medication interaction ingredients.

If validation fails:

1. Attempt a light repair only if the structure is close to valid.
2. Otherwise discard the invalid recipe.
3. If no generated recipes remain, return fallback recipes with `fallback_used = true`.

## 10. Serving Scaling Rules

Ingredient scaling should be deterministic.

Rules:

- `scale_factor = target_servings / default_servings`
- countable units round to nearest whole number:
  - piece
  - pieces
  - clove
  - cloves
  - egg
  - eggs
  - packet
  - packets
- measurable units can keep one decimal:
  - cup
  - cups
  - tbsp
  - tsp
  - oz
  - lb
  - g
  - ml
- if the scaled measurable quantity is a whole number, display it without a decimal.
- never mutate the stored recipe; return a scaled copy.

## 11. Caching Plan

Generated recipe cache key:

```text
patient_id + medication_name + condition_names + meal_type + available_ingredients + avoid_ingredients + dietary_pattern + cuisine_preference + max_cook_minutes + servings
```

Recommended initial cache:

- in-memory TTL cache
- max size: 50 to 100 entries
- TTL: 5 to 10 minutes

Why short-lived:

- patient context can change
- medication focus can change
- dietary preferences can change
- generated content should not feel stale

Later persistence can use database tables if recipe history becomes valuable.

## 12. Database Option For Later

Phase one can avoid migrations by using JSON and in-memory cache.

If persistence becomes necessary, add:

- `diet_recipes`
- `diet_recipe_generations`
- `diet_recipe_feedback`

Potential columns for `diet_recipes`:

- `id`
- `recipe_id`
- `patient_id`, nullable for curated global recipes
- `source`
- `title`
- `description`
- `default_servings`
- `cook_time`
- `meal_type`
- `ingredients_json`
- `instructions_json`
- `safety_notes_json`
- `condition_fit_json`
- `medication_fit_json`
- `avoid_flags_json`
- `image_url`
- `created_at`

Do not add database persistence until the API contract and UI behavior are stable.

## 13. Implementation Phases

### Phase 1: Curated Recipe Foundation

Backend:

1. Add recipe Pydantic models.
2. Add `src/cure_quest/data/diet_recipes.json`.
3. Add `RecipeStore`.
4. Add `DietAgent.list_curated_recipes`.
5. Add `DietAgent.get_recipe`.
6. Add `DietAgent.scale_recipe`.
7. Add `GET /diet/recipes`.
8. Add `GET /diet/recipes/{recipe_id}`.
9. Add tests for loading, missing files, invalid recipe ids, and scaling.

Frontend:

1. Add recipe TypeScript interfaces.
2. Add `fetchDietRecipes`.
3. Render a curated recipe grid below existing diet rules.
4. Add a recipe detail panel.
5. Add serving scaling in the detail panel using frontend calculations or a backend scale endpoint.

Acceptance criteria:

- The diet section shows curated recipes without model calls.
- Opening a recipe reveals ingredients and instructions.
- Serving changes update ingredient quantities.
- Existing diet support route still works.

### Phase 2: Generated Recipes

Backend:

1. Add `GenerateDietRecipesRequest`.
2. Add `GenerateDietRecipesResponse`.
3. Add `DietAgent.generate_recipes`.
4. Add strict JSON prompt builder.
5. Add generated recipe parser and validator.
6. Add deterministic fallback recipes.
7. Add safety annotation after generation.
8. Add `POST /diet/recipes/generate`.
9. Add unit tests for valid JSON, invalid JSON, timeout fallback, blocked ingredient handling, and medication rule flags.

Frontend:

1. Add generator controls.
2. Add `generateDietRecipes`.
3. Add loading state.
4. Add fallback-used notice.
5. Add error state.
6. Render generated recipes above curated recipes.

Acceptance criteria:

- The user can generate up to 3 recipes from medication and preference inputs.
- Invalid model output does not crash the route.
- Fallback recipes render when generation fails.
- Safety notes are visible in list and detail views.

### Phase 3: Images And Polish

Backend:

1. Add optional image fields to the response.
2. Add image generation only behind a feature flag.
3. Add image compression.
4. Add image cache.
5. Return recipes even if image generation fails.

Frontend:

1. Add stable image areas to cards.
2. Add placeholder visuals.
3. Render generated image when present.
4. Ensure text and layout do not shift when images load.

Acceptance criteria:

- Recipe cards have visual context.
- No blank or broken image areas.
- Recipe text loads before images.
- Image failures do not block recipe use.

### Phase 4: Safety Expansion

Backend:

1. Expand medication-food rule table.
2. Add condition-specific caution tags.
3. Optionally enrich medication food notes with label lookups.
4. Add high-risk caution behavior.
5. Log generation metadata for audit/debugging without storing sensitive prompt text unless explicitly required.

Frontend:

1. Make caution notes more visible.
2. Add "why this recipe" detail.
3. Add avoid-list chips.

Acceptance criteria:

- Recipes explain medication and condition fit.
- Caution tags are visible without causing alarmist copy.
- High-risk or uncertain cases avoid overconfident recommendations.

## 14. Testing Plan

### Backend Unit Tests

Add `tests/test_diet_recipes.py`.

Test cases:

- curated recipe JSON loads successfully
- missing recipe file returns an empty list or clear error depending on chosen behavior
- get recipe by id returns the correct recipe
- unknown recipe id returns 404 through the route
- ingredient scaling handles countable units
- ingredient scaling handles measurable units
- avoid ingredients are blocked
- medication-food rule flags grapefruit for statin-like medication names
- metformin rule adds with-food guidance
- IBS rule adds gentle-meal preference or caution
- invalid generated JSON falls back
- generated recipe with blocked ingredient is rejected or flagged

### API Tests

Route tests:

- `GET /diet/recipes`
- `GET /diet/recipes/{recipe_id}`
- `POST /diet/recipes/generate`
- malformed generate request
- generate request with no available ingredients
- generate request with avoid ingredients

### Frontend Checks

Run:

```powershell
npm run lint
npm run build
```

Manual UI checks:

- desktop recipe grid
- mobile recipe grid
- loading state
- empty state
- error state
- generated recipe detail
- curated recipe detail
- serving selector
- caution note readability
- image placeholder behavior

## 15. Accessibility Requirements

The recipe UI should include:

- labels for every input
- keyboard-focusable recipe cards or buttons
- visible focus styles
- semantic lists for ingredients and instructions
- no color-only safety signals
- descriptive image alt text
- accessible loading text
- no layout shift that moves focused controls unexpectedly

## 16. Observability

Add non-sensitive logs around:

- generation requested
- provider path used
- fallback used
- recipe count returned
- validation failures
- blocked ingredients found
- image generation skipped, succeeded, or failed

Avoid logging full patient context, full prompts, or generated text unless a debug flag is explicitly enabled.

## 17. File-Level Checklist

Backend files to add:

- `src/cure_quest/data/diet_recipes.json`
- `src/cure_quest/services/recipe_store.py`
- `src/cure_quest/services/recipe_generation.py`
- `tests/test_diet_recipes.py`

Backend files to update:

- `src/cure_quest/agents/diet.py`
- `src/cure_quest/agents/orchestrator.py`
- `src/cure_quest/api/models.py`
- `src/cure_quest/api/routes.py`
- `src/cure_quest/services/model_routing.py`, only if routing metadata should expose the recipe generator
- `pyproject.toml`, only if direct image generation or additional cache dependency is added

Frontend files to add:

- `frontend/src/components/diet/DietRecipeStudio.tsx`
- `frontend/src/components/diet/RecipeGeneratorPanel.tsx`
- `frontend/src/components/diet/RecipeGrid.tsx`
- `frontend/src/components/diet/RecipeCard.tsx`
- `frontend/src/components/diet/RecipeDetailPanel.tsx`
- `frontend/src/components/diet/SafetyNotes.tsx`

Frontend files to update:

- `frontend/src/lib/api.ts`
- `frontend/src/screens/CareMazeScreen.tsx`
- `frontend/src/index.css`, only for shared recipe-specific utilities that cannot be handled with local Tailwind classes

## 18. Rollout Order

Recommended order:

1. Add backend recipe models and curated JSON.
2. Add recipe store and scaling tests.
3. Add list/detail recipe API routes.
4. Render curated recipe grid in the frontend.
5. Add recipe detail panel with serving scaling.
6. Add generator request/response models.
7. Add generation service with strict parser and fallback.
8. Render generated recipes in the frontend.
9. Add safety notes and caution flags.
10. Add optional image handling.
11. Expand tests and manual QA.
12. Consider persistence only after the UX is stable.

## 19. Definition Of Done

The enhancement is done when:

- diet support still returns existing meal rules
- curated recipes are visible in the diet section
- generated recipes can be requested from the diet section
- generated recipes return structured ingredients and instructions
- recipes include medication and condition safety notes
- servings can be scaled
- model failures return useful fallback recipes
- no non-recipe commerce behavior is included
- no names, project labels, or branding from the reference are copied into code or user-facing text
- backend tests cover recipe store, scaling, generation fallback, and safety flags
- frontend build and type checks pass
