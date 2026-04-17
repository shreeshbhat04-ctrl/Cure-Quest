import re
from datetime import datetime

from sqlalchemy import select
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
from cure_quest.db.models import Patient, Prescription
from cure_quest.services.google_workspace import credentials_from_tokens
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
        import re
        profile = self.brain_gateway.get_patient_profile(patient_id)
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        all_tasks = self.routine.get_daily_routine()
        
        # Filter tasks using exact word boundaries so "Patient 1" doesn't match "Patient 12"
        patient_pattern = re.compile(rf"Patient {patient_id}\b", re.IGNORECASE)
        any_patient_pattern = re.compile(r"Patient \d+", re.IGNORECASE)
        
        routine_tasks = [
            task for task in all_tasks
            if patient_pattern.search(task.name)
            or not any_patient_pattern.search(task.name)
        ]
        
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

    def route_conversation(self, patient_id: int, message: str, db: Session | None = None) -> dict:
        profile = self.brain_gateway.get_patient_profile(patient_id)
        plan = self.communications.build_conversation_plan(message, profile=profile)
        tool_outcome = self._maybe_execute_conversation_tool(
            db=db,
            patient_id=patient_id,
            message=message,
            patient_name=None if profile is None else profile.full_name,
        )
        if tool_outcome is not None:
            plan["message"] = tool_outcome["message"]
            plan["execution_plan"] = [*plan["execution_plan"], *tool_outcome["execution_plan"]]
            plan["reason"] = f"{plan['reason']} {tool_outcome['reason']}".strip()
        return {
            "patient_id": patient_id,
            "profile": None if profile is None else profile.to_dict(),
            **plan,
        }

    def _maybe_execute_conversation_tool(
        self,
        db: Session | None,
        patient_id: int,
        message: str,
        patient_name: str | None,
    ) -> dict | None:
        if db is None:
            return None

        normalized = message.lower().strip()

        if self._is_calendar_request(normalized):
            return self._execute_calendar_request(db=db, patient_id=patient_id, patient_name=patient_name)

        if self._is_health_email_list_request(normalized):
            return self._execute_health_email_list(db=db, patient_id=patient_id)

        if self._is_send_email_request(normalized):
            return self._execute_send_email(db=db, patient_id=patient_id, message=message, patient_name=patient_name)

        if self._is_escalation_request(normalized):
            return self._execute_escalation(db=db, patient_id=patient_id, message=message)

        if self._is_drive_request(normalized):
            return self._execute_drive_request(db=db, patient_id=patient_id, normalized=normalized)

        if self._is_prescription_lookup_request(normalized):
            return self._execute_prescription_lookup(db=db, patient_id=patient_id)

        return None

    def _execute_calendar_request(self, db: Session, patient_id: int, patient_name: str | None) -> dict:
        summary = f"Doctor follow-up for {patient_name or f'patient {patient_id}'}"
        result = self.integrations.create_calendar_event(
            db=db,
            patient_id=patient_id,
            summary=summary,
            minutes_from_now=45,
            duration_minutes=30,
        )
        return {
            "message": (
                "I created a follow-up appointment on the connected calendar. "
                + (
                    f"Open it here: {result.get('htmlLink')}"
                    if result.get("htmlLink")
                    else "It was created with the default follow-up window."
                )
            ),
            "reason": "The message requested booking or scheduling a doctor follow-up.",
            "execution_plan": [
                "Create a calendar follow-up event through the connected calendar integration.",
            ],
        }

    def _execute_health_email_list(self, db: Session, patient_id: int) -> dict:
        patient = db.scalar(select(Patient).where(Patient.id == patient_id))
        if not patient or not patient.google_access_token:
            return {
                "message": "I can check health emails after Google Gmail is connected for this patient.",
                "reason": "Email lookup requires stored Google OAuth tokens.",
                "execution_plan": [
                    "Ask the user to connect Google Gmail before reading inbox messages.",
                ],
            }

        creds = credentials_from_tokens(
            access_token=patient.google_access_token,
            refresh_token=patient.google_refresh_token,
        )
        emails = self.integrations.list_health_emails(credentials=creds, max_results=5)
        if not emails:
            return {
                "message": "I checked the connected Gmail account and didn’t find recent health-related emails.",
                "reason": "The message asked to inspect recent health emails.",
                "execution_plan": [
                    "Query recent health-related Gmail messages for the connected patient account.",
                ],
            }

        preview = "; ".join(email.get("subject", "(no subject)") for email in emails[:3])
        return {
            "message": f"I checked the connected Gmail account. Recent health-related emails include: {preview}.",
            "reason": "The message asked to inspect recent health emails.",
            "execution_plan": [
                "Query recent health-related Gmail messages for the connected patient account.",
            ],
        }

    def _execute_send_email(self, db: Session, patient_id: int, message: str, patient_name: str | None) -> dict:
        patient = db.scalar(select(Patient).where(Patient.id == patient_id))
        target_email_match = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", message)
        if target_email_match is None:
            return {
                "message": "I can send an email, but I need the recipient email address in the message.",
                "reason": "Email sending requires an explicit recipient address.",
                "execution_plan": [
                    "Ask for a concrete recipient email address before sending care summary mail.",
                ],
            }
        if not patient or not patient.google_access_token:
            return {
                "message": "I can send email after Google Gmail is connected for this patient.",
                "reason": "Email sending requires stored Google OAuth tokens.",
                "execution_plan": [
                    "Ask the user to connect Google Gmail before sending mail.",
                ],
            }

        target_email = target_email_match.group(0)
        creds = credentials_from_tokens(
            access_token=patient.google_access_token,
            refresh_token=patient.google_refresh_token,
        )
        subject = f"Cure-Quest care summary for {patient_name or f'patient {patient_id}'}"
        body_html = self._build_professional_care_email(
            db=db,
            patient_id=patient_id,
            patient_name=patient_name,
            patient_summary=patient.summary,
            message=message,
        )
        result = self.integrations.send_care_email(
            to=target_email,
            subject=subject,
            body_html=body_html,
            credentials=creds,
        )
        if result.get("sent"):
            return {
                "message": f"I sent the care summary email to {target_email}.",
                "reason": "The message requested sending a care summary email.",
                "execution_plan": [
                    "Send the care summary through the connected Gmail integration.",
                ],
            }
        return {
            "message": f"I tried to send the email to {target_email}, but it failed: {result.get('error') or 'unknown error'}.",
            "reason": "The message requested sending a care summary email.",
            "execution_plan": [
                "Attempt to send the care summary through the connected Gmail integration.",
            ],
        }

    def _build_professional_care_email(
        self,
        db: Session,
        patient_id: int,
        patient_name: str | None,
        patient_summary: str | None,
        message: str,
    ) -> str:
        conditions = self.temporal_memory.get_relevant_conditions(patient_id)
        condition_names = [item.name for item in conditions if item.name][:3]
        recent_prescriptions = db.scalars(
            select(Prescription)
            .where(Prescription.patient_id == patient_id)
            .order_by(Prescription.created_at.desc())
        ).all()[:3]

        clean_request = re.sub(r"[\w.\-+]+@[\w.\-]+\.\w+", "[recipient]", message).strip()
        recipient_name = patient_name or f"patient {patient_id}"
        sent_on = datetime.now().strftime("%Y-%m-%d")

        sections: list[str] = [
            "<p>Dear Care Team,</p>",
            (
                f"<p>Please find a brief care update for <strong>{recipient_name}</strong> "
                f"as of {sent_on}.</p>"
            ),
        ]

        if patient_summary:
            sections.append(f"<p><strong>Patient Summary:</strong> {patient_summary}</p>")

        if condition_names:
            sections.append(
                "<p><strong>Relevant Conditions:</strong> "
                + ", ".join(condition_names)
                + "</p>"
            )

        if recent_prescriptions:
            medication_summary = ", ".join(
                f"{item.medication_name}{f' {item.dosage}' if item.dosage else ''}".strip()
                for item in recent_prescriptions
            )
            sections.append(f"<p><strong>Recent Prescription History:</strong> {medication_summary}</p>")

        sections.append(f"<p><strong>Patient Request:</strong> {clean_request}</p>")
        sections.extend(
            [
                "<p>Please review and advise if any clinical follow-up is recommended.</p>",
                "<p>Regards,<br>Cure-Quest Assistant</p>",
                "<p><em>This message is generated from the patient support workflow for care coordination.</em></p>",
            ]
        )
        return "".join(sections)

    def _execute_escalation(self, db: Session, patient_id: int, message: str) -> dict:
        case = self.hitl.create_case(db, patient_id, "doctor_review", message)
        return {
            "message": (
                "I created a doctor handoff for review."
                + (
                    f" Open it here: {case.external_ticket_url}"
                    if case.external_ticket_url
                    else ""
                )
            ),
            "reason": "The message requested escalation or doctor handoff.",
            "execution_plan": [
                "Create a doctor-review case through the escalation workflow.",
            ],
        }

    def _execute_prescription_lookup(self, db: Session, patient_id: int) -> dict:
        prescriptions = db.scalars(
            select(Prescription)
            .where(Prescription.patient_id == patient_id)
            .order_by(Prescription.created_at.desc())
        ).all()

        if not prescriptions:
            return {
                "message": "I don’t see any stored prescriptions for this patient yet.",
                "reason": "The message asked for the current prescription list.",
                "execution_plan": [
                    "Look up stored prescriptions from the patient workspace.",
                ],
            }

        recent = prescriptions[:3]
        summary = "; ".join(
            f"{item.medication_name}{f' {item.dosage}' if item.dosage else ''}".strip()
            for item in recent
        )
        return {
            "message": f"Here are the latest stored prescriptions: {summary}.",
            "reason": "The message asked for the current prescription list.",
            "execution_plan": [
                "Look up stored prescriptions from the patient workspace.",
            ],
        }

    def _execute_drive_request(self, db: Session, patient_id: int, normalized: str) -> dict:
        if self._is_drive_upload_request(normalized):
            return {
                "message": "I can upload to Drive when a file is attached, but chat and voice requests do not include a document payload yet.",
                "reason": "Drive upload from conversation needs an attached file or explicit file path.",
                "execution_plan": [
                    "Explain that Drive upload needs an attached file or explicit document reference.",
                ],
            }

        patient = db.scalar(select(Patient).where(Patient.id == patient_id))
        if not patient or not patient.google_access_token:
            return {
                "message": "I can check Drive after Google Drive is connected for this patient.",
                "reason": "Drive listing requires stored Google OAuth tokens.",
                "execution_plan": [
                    "Ask the user to connect Google Drive before browsing files.",
                ],
            }

        creds = credentials_from_tokens(
            access_token=patient.google_access_token,
            refresh_token=patient.google_refresh_token,
        )
        files = self.integrations.list_drive_files(credentials=creds, max_results=5)
        prescription_links = db.scalars(
            select(Prescription)
            .where(Prescription.patient_id == patient_id, Prescription.document_drive_file_url.is_not(None))
            .order_by(Prescription.created_at.desc())
        ).all()

        details: list[str] = []
        if files:
            file_summary = "; ".join(item.get("name", "Unnamed file") for item in files[:3])
            details.append(f"Recent Drive files: {file_summary}.")
        if prescription_links:
            prescription_summary = "; ".join(
                f"{item.medication_name}: {item.document_drive_file_url}"
                for item in prescription_links[:2]
            )
            details.append(f"Prescription docs: {prescription_summary}.")

        if not details:
            details.append("I checked Drive, but I didn’t find recent accessible files or stored prescription documents.")

        return {
            "message": " ".join(details),
            "reason": "The message requested Drive access or Drive-backed prescription references.",
            "execution_plan": [
                "Query recent accessible files from the connected Google Drive account.",
                "Cross-reference stored prescription documents with Drive links in the patient workspace.",
            ],
        }

    @staticmethod
    def _is_calendar_request(normalized: str) -> bool:
        schedule_terms = ("book", "schedule", "set up", "create")
        appointment_terms = ("appointment", "follow-up", "doctor visit", "calendar event", "meeting")
        return any(term in normalized for term in schedule_terms) and any(term in normalized for term in appointment_terms)

    @staticmethod
    def _is_health_email_list_request(normalized: str) -> bool:
        email_terms = ("email", "emails", "gmail", "inbox", "mail")
        lookup_terms = ("check", "show", "list", "read", "recent", "latest")
        return any(term in normalized for term in email_terms) and any(term in normalized for term in lookup_terms)

    @staticmethod
    def _is_send_email_request(normalized: str) -> bool:
        return ("send" in normalized or "email" in normalized) and ("@" in normalized or "mail to" in normalized)

    @staticmethod
    def _is_escalation_request(normalized: str) -> bool:
        escalation_terms = ("escalate", "handoff", "send to doctor", "doctor review", "send doctor")
        return any(term in normalized for term in escalation_terms)

    @staticmethod
    def _is_drive_request(normalized: str) -> bool:
        drive_terms = ("drive", "upload", "save file", "save to google drive", "google drive", "drive files", "drive documents")
        return any(term in normalized for term in drive_terms)

    @staticmethod
    def _is_drive_upload_request(normalized: str) -> bool:
        upload_terms = ("upload", "save file", "save to google drive")
        return any(term in normalized for term in upload_terms)

    @staticmethod
    def _is_prescription_lookup_request(normalized: str) -> bool:
        prescription_terms = ("prescription", "prescriptions", "medication list", "medicine list", "current meds", "current medication")
        lookup_terms = ("what", "show", "list", "check", "review", "current")
        return any(term in normalized for term in prescription_terms) and any(term in normalized for term in lookup_terms)

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
