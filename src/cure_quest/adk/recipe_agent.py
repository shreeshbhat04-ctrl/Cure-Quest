from google.adk.agents import LlmAgent

from cure_quest.config import get_settings

settings = get_settings()

recipe_agent = LlmAgent(
    model=settings.gemini_fast_model_id,
    name="cure_quest_recipe_agent",
    description="Generates safe, ingredient-based recipes for Cure-Quest diet workflows.",
    instruction=(
        "You are the Cure-Quest recipe generation ADK agent. "
        "When given ingredients, meal type, medication, and conditions, produce practical recipes as JSON only. "
        "Each recipe must include title, description, default_servings, cook_time, ingredients, instructions, "
        "safety_notes, condition_fit, medication_fit, and why_it_fits. "
        "Avoid cure claims and apply conservative medication-aware guidance."
    ),
)
