from cure_quest.adapters.formulary import MockFormularyAdapter
from cure_quest.api.models import AlternativeCandidate
from cure_quest.services.brain import BrainCondition


class FormularyAgent:
    def __init__(self, formulary_adapter: MockFormularyAdapter | None = None) -> None:
        self.formulary_adapter = formulary_adapter or MockFormularyAdapter()

    def check_alternatives(self, medication_name: str, conditions: list[BrainCondition]) -> tuple[list[AlternativeCandidate], bool, str]:
        condition_names = {condition.name.lower() for condition in conditions}
        candidates: list[AlternativeCandidate] = []
        escalation_required = False

        for record in self.formulary_adapter.find_alternatives(medication_name):
            safety_note = "No known issue from demo context."
            if "ibs" in condition_names and "extended" in record.formulation_note.lower():
                safety_note = "Extended-release option may irritate active IBS. Doctor review required."
                escalation_required = True
            candidates.append(
                AlternativeCandidate(
                    name=record.name,
                    formulation_note=record.formulation_note,
                    stock_status=record.stock_status,
                    safety_note=safety_note,
                )
            )

        summary = "Escalation required because a candidate needs clinician review." if escalation_required else "No blocking safety issues from demo context."
        return candidates, escalation_required, summary
