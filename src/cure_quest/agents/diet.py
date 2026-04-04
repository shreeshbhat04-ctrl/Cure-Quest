from cure_quest.api.models import AlternativeCandidate
from cure_quest.services.brain import BrainCondition


class DietAgent:
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
