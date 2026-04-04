from sqlalchemy.orm import Session

from cure_quest.agents.communications import CommunicationsAgent
from cure_quest.agents.diet import DietAgent
from cure_quest.agents.documents import DocumentAgent
from cure_quest.agents.formulary import FormularyAgent
from cure_quest.agents.hitl import HITLAgent
from cure_quest.agents.integrations import IntegrationAgent
from cure_quest.agents.intake import IntakeAgent
from cure_quest.agents.routine import RoutineAgent
from cure_quest.agents.temporal_memory import TemporalMemoryAgent
from cure_quest.adapters.brain import BrainGateway, build_brain_gateway
from cure_quest.services.model_routing import ModelRoutingService


class Orchestrator:
    def __init__(self, brain_gateway: BrainGateway | None = None) -> None:
        shared_brain_gateway = brain_gateway or build_brain_gateway()
        self.intake = IntakeAgent()
        self.temporal_memory = TemporalMemoryAgent(brain_gateway=shared_brain_gateway)
        self.formulary = FormularyAgent()
        self.hitl = HITLAgent()
        self.routine = RoutineAgent()
        self.diet = DietAgent()
        self.documents = DocumentAgent()
        self.integrations = IntegrationAgent()
        self.communications = CommunicationsAgent()
        self.brain_gateway = shared_brain_gateway
        self.model_routing = ModelRoutingService()

    def evaluate_alternatives(self, patient_id: int, unavailable_medication: str):
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        return self.formulary.check_alternatives(unavailable_medication, conditions)

    def build_daily_checkin(self, patient_id: int) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        routine_tasks = self.routine.get_daily_routine()
        message = self.communications.compose_daily_checkin(profile, conditions, routine_tasks)
        return {
            "profile": None if profile is None else profile.to_dict(),
            "conditions": [item.to_dict() for item in conditions],
            "routine_tasks": [task.__dict__ for task in routine_tasks],
            "message": message,
        }

    def build_diet_and_pharmacy_support(self, patient_id: int, medication_name: str | None, location_query: str | None) -> dict:
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        pharmacy_result = self.integrations.search_nearby_pharmacies(location_query) if location_query else {"provider": "disabled", "pharmacies": []}
        pharmacy_names = [item["name"] for item in pharmacy_result.get("pharmacies", [])[:3] if item.get("name")]
        pharmacy_summary = ", ".join(pharmacy_names) if pharmacy_names else None
        diet_plan = self.diet.build_diet_support_plan(conditions, medication_name=medication_name, pharmacy_summary=pharmacy_summary)
        return {
            "conditions": [item.to_dict() for item in conditions],
            "diet_plan": diet_plan,
            "pharmacy_result": pharmacy_result,
        }

    def build_document_pipeline(self, patient_id: int, file_path: str, raw_text_hint: str | None = None, prescription_id: int | None = None) -> dict:
        return self.documents.build_document_intake_plan(
            patient_id=patient_id,
            file_path=file_path,
            raw_text_hint=raw_text_hint,
            prescription_id=prescription_id,
        )

    def route_conversation(self, patient_id: int, message: str) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        plan = self.communications.build_conversation_plan(message)
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            **plan,
        }

    def route_medical_input(self, patient_id: int, query_text: str | None = None, file_path: str | None = None) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        route = self.model_routing.route_medical_input(query_text=query_text, file_path=file_path)
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            "query_text": query_text,
            "file_path": file_path,
            **route,
        }

    def store_medical_memory(
        self,
        db,
        patient_id: int,
        source_type: str,
        query_text: str | None = None,
        file_path: str | None = None,
        drive_file_id: str | None = None,
        drive_file_url: str | None = None,
        metadata: dict | None = None,
        use_live_embedding: bool = False,
    ) -> dict:
        route = self.model_routing.route_medical_input(query_text=query_text, file_path=file_path)
        result = self.integrations.store_medical_memory(
            db=db,
            patient_id=patient_id,
            source_type=source_type,
            query_text=query_text,
            file_path=file_path,
            drive_file_id=drive_file_id,
            drive_file_url=drive_file_url,
            use_live_embedding=use_live_embedding,
            metadata={
                "route_type": route["route_type"],
                "route_reason": route["reason"],
                **(metadata or {}),
            },
        )
        return {
            **result,
            "route_type": route["route_type"],
            "route_reason": route["reason"],
        }

    def search_medical_memory(self, db, patient_id: int, query_text: str, modality: str | None = None, limit: int = 5) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        results = self.integrations.search_medical_memory(
            db=db,
            patient_id=patient_id,
            query_text=query_text,
            modality=modality,
            limit=limit,
        )
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            **results,
        }

    def run_medgemma(self, patient_id: int, prompt: str, image_path: str | None = None, max_new_tokens: int = 128) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        result = self.integrations.run_medgemma(prompt=prompt, image_path=image_path, max_new_tokens=max_new_tokens)
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            **result,
        }

    def run_medsiglip_classification(self, patient_id: int, image_path: str, candidate_labels: list[str]) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        result = self.integrations.run_medsiglip_classification(image_path=image_path, candidate_labels=candidate_labels)
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            **result,
        }

    def get_orchestration_manifest(self, patient_id: int) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        routine_tasks = self.routine.get_daily_routine()
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            "conditions": [item.to_dict() for item in conditions],
            "routine_tasks": [task.__dict__ for task in routine_tasks],
            "agent_manifest": self.model_routing.get_model_manifest(),
            "trigger_manifest": {
                "general_conversation": "Gemini 3.1 Flash handles supportive and everyday conversation.",
                "medical_text_query": "MedGemma handles symptom, disease, medicine, and clinical text queries.",
                "medical_image_upload": "MedSigLIP handles the uploaded image first, then MedGemma performs medical reasoning.",
            },
        }

    def run_document_intake_flow(
        self,
        db: Session,
        patient_id: int,
        image_reference: str | None = None,
        raw_text_hint: str | None = None,
        document_file_path: str | None = None,
        pharmacy_location_query: str | None = None,
        create_calendar_event: bool = True,
    ) -> dict:
        self.integrations.log_integration_event("workflow_started", {"patient_id": patient_id, "flow": "document_intake"})
        prescription = self.intake.scan_prescription(
            db=db,
            patient_id=patient_id,
            image_reference=image_reference,
            raw_text_hint=raw_text_hint,
        )

        drive_result = None
        if document_file_path:
            try:
                drive_result = self.integrations.upload_document(
                    db=db,
                    patient_id=patient_id,
                    file_path=document_file_path,
                    mime_type="application/pdf" if document_file_path.lower().endswith(".pdf") else "application/octet-stream",
                    prescription_id=prescription.id,
                )
            except Exception as error:
                drive_result = {"error": str(error)}

        memory_result = self.store_medical_memory(
            db=db,
            patient_id=patient_id,
            source_type="document_intake_flow",
            query_text=prescription.raw_text,
            file_path=document_file_path or image_reference,
            drive_file_id=None if not drive_result else drive_result.get("id"),
            drive_file_url=None if not drive_result else drive_result.get("webViewLink"),
            use_live_embedding=True,
            metadata={"prescription_id": prescription.id},
        )

        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        candidates, escalation_required, safety_summary = self.formulary.check_alternatives(prescription.medication_name, conditions)
        diet_support = self.diet.annotate_alternatives(candidates, conditions)
        pharmacy_result = None
        if pharmacy_location_query:
            try:
                pharmacy_result = self.integrations.search_nearby_pharmacies(pharmacy_location_query)
            except Exception as error:
                pharmacy_result = {"provider": "error", "error": str(error), "pharmacies": []}

        case = None
        calendar_result = None
        flow_notes: list[str] = []
        if prescription.review_status == "manual_review_required":
            flow_notes.append("OCR confidence below threshold. Manual review required.")
            escalation_required = True
        if escalation_required:
            report = self.hitl.build_detailed_report(db, patient_id, f"{safety_summary}\nMedication: {prescription.medication_name}")
            case = self.hitl.create_case(db, patient_id, "doctor_review", report)
            flow_notes.append("HITL case created.")
            if create_calendar_event:
                try:
                    calendar_result = self.integrations.create_calendar_event(
                        db=db,
                        patient_id=patient_id,
                        summary=f"Doctor follow-up for {prescription.medication_name}",
                        minutes_from_now=45,
                        duration_minutes=30,
                        escalation_case_id=case.id,
                    )
                except Exception as error:
                    calendar_result = {"error": str(error)}

        notification = self.communications.notify(
            db=db,
            patient_id=patient_id,
            channel="mock_email",
            message_type="workflow_update",
            message_body=(
                "We reviewed your uploaded medication details. "
                + ("A doctor follow-up has been prepared." if escalation_required else "No urgent review is needed right now.")
            ),
        )

        self.integrations.log_integration_event(
            "document_intake_flow_completed",
            {
                "patient_id": patient_id,
                "prescription_id": prescription.id,
                "escalation_required": escalation_required,
                "case_id": None if case is None else case.id,
                "calendar_event_id": None if not calendar_result else calendar_result.get("id"),
                "memory_id": memory_result["memory_id"],
            },
        )

        return {
            "patient_id": patient_id,
            "prescription": {
                "id": prescription.id,
                "medication_name": prescription.medication_name,
                "dosage": prescription.dosage,
                "instructions": prescription.instructions,
                "confidence_score": prescription.confidence_score,
                "review_status": prescription.review_status,
            },
            "document_pipeline": self.build_document_pipeline(
                patient_id=patient_id,
                file_path=document_file_path or image_reference or "inline-input",
                raw_text_hint=raw_text_hint,
                prescription_id=prescription.id,
            ),
            "drive_result": drive_result,
            "memory_result": memory_result,
            "alternatives": [candidate.model_dump() for candidate in candidates],
            "diet_support": diet_support,
            "pharmacy_result": pharmacy_result,
            "escalation_required": escalation_required,
            "safety_summary": safety_summary,
            "case": None
            if case is None
            else {
                "case_id": case.id,
                "status": case.status,
                "external_ticket_id": case.external_ticket_id,
                "external_ticket_url": case.external_ticket_url,
            },
            "calendar_result": calendar_result,
            "notification": {
                "notification_id": notification.id,
                "delivery_status": notification.delivery_status,
            },
            "flow_notes": flow_notes,
        }

    def run_routine_automation(self, db: Session, patient_id: int) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        snapshot = self.routine.get_routine_snapshot()
        message = self.communications.compose_daily_checkin(profile, conditions, snapshot["tasks"])
        case = None
        if snapshot["risk_level"] == "high":
            report = self.hitl.build_detailed_report(db, patient_id, snapshot["routine_summary"])
            case = self.hitl.create_case(db, patient_id, "routine_nonadherence", report)

        self.integrations.log_integration_event(
            "routine_automation_evaluated",
            {
                "patient_id": patient_id,
                "risk_level": snapshot["risk_level"],
                "overdue_count": snapshot["overdue_count"],
                "case_id": None if case is None else case.id,
            },
        )
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            "routine_tasks": [task.__dict__ for task in snapshot["tasks"]],
            "routine_summary": snapshot["routine_summary"],
            "risk_level": snapshot["risk_level"],
            "overdue_count": snapshot["overdue_count"],
            "due_today_count": snapshot["due_today_count"],
            "message": message,
            "case": None
            if case is None
            else {
                "case_id": case.id,
                "status": case.status,
                "external_ticket_id": case.external_ticket_id,
                "external_ticket_url": case.external_ticket_url,
            },
        }
