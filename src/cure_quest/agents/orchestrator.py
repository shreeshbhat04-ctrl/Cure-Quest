from cure_quest.agents.communications import CommunicationsAgent
from cure_quest.agents.formulary import FormularyAgent
from cure_quest.agents.hitl import HITLAgent
from cure_quest.agents.intake import IntakeAgent
from cure_quest.agents.temporal_memory import TemporalMemoryAgent
from cure_quest.adapters.brain import BrainGateway, build_brain_gateway


class Orchestrator:
    def __init__(self, brain_gateway: BrainGateway | None = None) -> None:
        shared_brain_gateway = brain_gateway or build_brain_gateway()
        self.intake = IntakeAgent()
        self.temporal_memory = TemporalMemoryAgent(brain_gateway=shared_brain_gateway)
        self.formulary = FormularyAgent()
        self.hitl = HITLAgent()
        self.communications = CommunicationsAgent()
        self.brain_gateway = shared_brain_gateway

    def evaluate_alternatives(self, patient_id: int, unavailable_medication: str):
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        return self.formulary.check_alternatives(unavailable_medication, conditions)
