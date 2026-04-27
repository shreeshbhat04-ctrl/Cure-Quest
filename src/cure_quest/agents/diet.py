from __future__ import annotations

import asyncio
import json
from typing import Any

from cure_quest.api.models import AlternativeCandidate
from cure_quest.config import get_settings
from cure_quest.services.brain import BrainCondition
from cure_quest.services.recipe_store import RecipeStore

try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types as genai_types

    ADK_AVAILABLE = True
except Exception:
    ADK_AVAILABLE = False


class DietAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.recipe_store = RecipeStore()
        self.adk_available = ADK_AVAILABLE
        self._recipe_agent = self._build_recipe_agent() if self.adk_available else None

    def _build_recipe_agent(self):
        return Agent(
            name="diet_recipe_generator",
            model=self.settings.gemini_fast_model_id,
            description="Generates medication-aware recipes from provided ingredients.",
            instruction=(
                "You are a clinical-safe recipe assistant. Return only JSON with a top-level `recipes` array. "
                "Each recipe must include recipe_id, title, description, default_servings, cook_time, meal_type, "
                "ingredients, instructions, condition_fit, medication_fit, avoid_flags, and why_it_fits. "
                "Never claim treatment or cure. Keep guidance practical and conservative."
            ),
        )

    def build_diet_support_plan(
        self,
        conditions: list[BrainCondition],
        medication_name: str | None = None,
        pharmacy_summary: str | None = None,
    ) -> dict:
        condition_names = {item.name.lower() for item in conditions}
        meal_rules: list[str] = [
            "Prioritize regular meal timings and hydration.",
            "Avoid abrupt meal skipping when medicines are being taken regularly.",
        ]

        if "ibs" in condition_names:
            meal_rules.append("Prefer gentle, low-irritation meals and avoid known IBS triggers.")
        if medication_name and "statin" in medication_name.lower():
            meal_rules.append("Avoid grapefruit while this medication is active.")
        if medication_name and "metformin" in medication_name.lower():
            meal_rules.append("Take medication with meals to reduce stomach irritation.")

        return {
            "medication_name": medication_name,
            "meal_rules": meal_rules,
            "pharmacy_summary": pharmacy_summary,
            "plan_summary": " ".join(meal_rules[:3]),
        }

    def list_curated_recipes(
        self,
        meal_type: str | None = None,
        medication_name: str | None = None,
        conditions: list[BrainCondition] | None = None,
    ) -> list[dict]:
        conditions = conditions or []
        recipes = self.recipe_store.list_recipes(meal_type=meal_type)
        return [
            self.apply_safety_rules(
                recipe=recipe,
                conditions=conditions,
                medication_name=medication_name,
                avoid_ingredients=[],
            )
            for recipe in recipes
        ]

    def get_recipe(self, recipe_id: str) -> dict | None:
        return self.recipe_store.get_recipe(recipe_id)

    def scale_recipe(
        self,
        recipe_id: str,
        servings: int,
        conditions: list[BrainCondition],
        medication_name: str | None,
    ) -> dict | None:
        recipe = self.recipe_store.get_recipe(recipe_id)
        if recipe is None:
            return None
        scaled = self.recipe_store.scale_recipe(recipe, target_servings=servings)
        return self.apply_safety_rules(
            recipe=scaled,
            conditions=conditions,
            medication_name=medication_name,
            avoid_ingredients=[],
        )

    def generate_recipes(
        self,
        conditions: list[BrainCondition],
        medication_name: str | None,
        preferences: dict,
    ) -> dict:
        count = int(preferences.get("count", 3) or 3)
        count = max(1, min(count, 3))
        avoid_ingredients = [str(item).strip() for item in preferences.get("avoid_ingredients", []) if str(item).strip()]
        meal_type = str(preferences.get("meal_type", "any"))

        generated: list[dict] = []
        fallback_used = False

        if self._recipe_agent is not None:
            generated = self._generate_with_adk(
                conditions=conditions,
                medication_name=medication_name,
                preferences=preferences,
            )

        safe_generated: list[dict] = []
        for recipe in generated:
            if self._recipe_contains_blocked(recipe, medication_name, avoid_ingredients):
                continue
            safe_generated.append(
                self.apply_safety_rules(
                    recipe=recipe,
                    conditions=conditions,
                    medication_name=medication_name,
                    avoid_ingredients=avoid_ingredients,
                )
            )

        if not safe_generated:
            fallback_used = True
            curated = self.list_curated_recipes(
                meal_type=meal_type,
                medication_name=medication_name,
                conditions=conditions,
            )
            safe_generated = curated[:count]
            for recipe in safe_generated:
                recipe["source"] = "generated"

        condition_names = [item.name for item in conditions]
        summary_chunks = [
            "Recipes generated with medication-aware safety checks.",
        ]
        if condition_names:
            summary_chunks.append(f"Condition context: {', '.join(condition_names)}.")
        if medication_name:
            summary_chunks.append(f"Medication focus: {medication_name}.")
        if fallback_used:
            summary_chunks.append("Fallback curated recipes were returned.")

        return {
            "conditions": [item.to_dict() for item in conditions],
            "medication_name": medication_name,
            "recipes": safe_generated[:count],
            "fallback_used": fallback_used,
            "safety_summary": " ".join(summary_chunks),
        }

    def _generate_with_adk(
        self,
        conditions: list[BrainCondition],
        medication_name: str | None,
        preferences: dict,
    ) -> list[dict]:
        if self._recipe_agent is None:
            return []

        prompt = self._build_generation_prompt(
            conditions=conditions,
            medication_name=medication_name,
            preferences=preferences,
        )

        try:
            return asyncio.run(self._run_adk_generation(prompt))
        except Exception:
            return []

    async def _run_adk_generation(self, prompt: str) -> list[dict]:
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="cure_quest_recipe_service",
            user_id="diet_user",
            session_id="diet_session",
        )

        runner = Runner(
            agent=self._recipe_agent,
            app_name="cure_quest_recipe_service",
            session_service=session_service,
        )

        content = genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])
        events = runner.run(user_id="diet_user", session_id="diet_session", new_message=content)

        final_response = ""
        for event in events:
            if hasattr(event, "is_final_response") and event.is_final_response():
                if hasattr(event, "content") and event.content and getattr(event.content, "parts", None):
                    final_response = event.content.parts[0].text or ""
                    break

        return self._parse_generated_response(final_response)

    def _parse_generated_response(self, raw_text: str) -> list[dict]:
        if not raw_text:
            return []

        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            return []

        recipes: list[dict]
        if isinstance(payload, dict):
            recipes = payload.get("recipes", [])
        elif isinstance(payload, list):
            recipes = payload
        else:
            recipes = []

        normalized: list[dict] = []
        for idx, recipe in enumerate(recipes):
            if not isinstance(recipe, dict):
                continue
            normalized.append(self._normalize_generated_recipe(recipe, idx))
        return normalized

    def _normalize_generated_recipe(self, recipe: dict, index: int) -> dict:
        ingredients = recipe.get("ingredients", [])
        normalized_ingredients: list[dict] = []
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                if not isinstance(ingredient, dict):
                    continue
                normalized_ingredients.append(
                    {
                        "name": str(ingredient.get("name", "Ingredient")).strip(),
                        "quantity": float(ingredient.get("quantity", 1)),
                        "unit": str(ingredient.get("unit", "unit")).strip(),
                    }
                )

        instructions = recipe.get("instructions", [])
        if not isinstance(instructions, list):
            instructions = []

        return {
            "recipe_id": str(recipe.get("recipe_id") or f"generated_recipe_{index + 1}"),
            "source": "generated",
            "title": str(recipe.get("title", f"Generated Recipe {index + 1}")).strip(),
            "description": str(recipe.get("description", "Personalized meal suggestion.")).strip(),
            "default_servings": int(recipe.get("default_servings", 2) or 2),
            "cook_time": str(recipe.get("cook_time", "20 minutes")).strip(),
            "meal_type": recipe.get("meal_type"),
            "ingredients": normalized_ingredients,
            "instructions": [str(step).strip() for step in instructions if str(step).strip()],
            "safety_notes": recipe.get("safety_notes", []),
            "condition_fit": recipe.get("condition_fit", []),
            "medication_fit": recipe.get("medication_fit", []),
            "avoid_flags": recipe.get("avoid_flags", []),
            "why_it_fits": str(recipe.get("why_it_fits", "Built from provided ingredients and safety context.")).strip(),
            "dietary_pattern": recipe.get("dietary_pattern"),
            "cuisine_preference": recipe.get("cuisine_preference"),
            "image_url": recipe.get("image_url"),
            "image_status": recipe.get("image_status", "unavailable"),
        }

    def _build_generation_prompt(
        self,
        conditions: list[BrainCondition],
        medication_name: str | None,
        preferences: dict,
    ) -> str:
        condition_names = [item.name for item in conditions]
        return (
            "Generate up to 3 practical recipes and return ONLY valid JSON in this shape: "
            "{\"recipes\": [{recipe_id,title,description,default_servings,cook_time,meal_type,"
            "ingredients:[{name,quantity,unit}],instructions:[...],condition_fit:[...],medication_fit:[...],"
            "avoid_flags:[...],why_it_fits,dietary_pattern,cuisine_preference,image_url,image_status}]}. "
            "Do not include markdown, prose, or medical cure claims. "
            f"Conditions: {condition_names}. "
            f"Medication: {medication_name}. "
            f"Meal type: {preferences.get('meal_type')}. "
            f"Available ingredients: {preferences.get('available_ingredients', [])}. "
            f"Avoid ingredients: {preferences.get('avoid_ingredients', [])}. "
            f"Dietary pattern: {preferences.get('dietary_pattern')}. "
            f"Cuisine preference: {preferences.get('cuisine_preference')}. "
            f"Max cook minutes: {preferences.get('max_cook_minutes')}. "
            f"Servings: {preferences.get('servings')}"
        )

    def _recipe_contains_blocked(
        self,
        recipe: dict,
        medication_name: str | None,
        avoid_ingredients: list[str],
    ) -> bool:
        blocked = {item.lower() for item in avoid_ingredients}
        if medication_name and "statin" in medication_name.lower():
            blocked.update({"grapefruit", "grapefruit juice"})

        ingredient_names = [
            str(item.get("name", "")).lower().strip()
            for item in recipe.get("ingredients", [])
            if isinstance(item, dict)
        ]
        for ingredient_name in ingredient_names:
            for blocked_item in blocked:
                if blocked_item and blocked_item in ingredient_name:
                    return True
        return False

    def apply_safety_rules(
        self,
        recipe: dict,
        conditions: list[BrainCondition],
        medication_name: str | None,
        avoid_ingredients: list[str],
    ) -> dict:
        adjusted = dict(recipe)
        adjusted.setdefault("safety_notes", [])
        adjusted.setdefault("condition_fit", [])
        adjusted.setdefault("medication_fit", [])
        adjusted.setdefault("avoid_flags", [])

        condition_names = {item.name.lower() for item in conditions}

        ingredient_names = [
            str(item.get("name", "")).lower().strip()
            for item in adjusted.get("ingredients", [])
            if isinstance(item, dict)
        ]

        if "ibs" in condition_names and any(token in " ".join(ingredient_names) for token in ("chilli", "spicy", "pepper")):
            adjusted["safety_notes"].append(
                {
                    "severity": "caution",
                    "message": "Use milder seasoning during IBS flares.",
                    "related_to": "ibs",
                }
            )

        if medication_name and "metformin" in medication_name.lower():
            adjusted["safety_notes"].append(
                {
                    "severity": "info",
                    "message": "Taking metformin with meals can reduce stomach irritation.",
                    "related_to": "metformin",
                }
            )
            adjusted["medication_fit"].append("take with food")

        blocked_mentions = [item for item in avoid_ingredients if item.lower() in " ".join(ingredient_names)]
        if blocked_mentions:
            adjusted["avoid_flags"].extend(sorted({item.lower() for item in blocked_mentions}))

        if not adjusted.get("why_it_fits"):
            adjusted["why_it_fits"] = "Recipe selected for practical preparation and conservative safety context."

        return adjusted

    def annotate_alternatives(
        self,
        candidates: list[AlternativeCandidate],
        conditions: list[BrainCondition],
    ) -> dict:
        plan = self.build_diet_support_plan(conditions)
        return {
            "candidates": [candidate.model_dump() for candidate in candidates],
            "diet_support_plan": plan,
        }
