import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
import time

from cure_quest.adapters.analytics import BigQueryAnalyticsAdapter
from cure_quest.adapters.calendar import GoogleCalendarAdapter
from cure_quest.adapters.drive import GoogleDriveAdapter
from cure_quest.adapters.gmail import GoogleGmailAdapter
from cure_quest.adapters.medical_memory import MedicalMemoryAdapter
from cure_quest.adapters.openfda import OpenFDAAdapter
from cure_quest.adapters.pharmacy import PharmacySearchAdapter
from cure_quest.adapters.speech import GoogleSpeechAdapter
from cure_quest.db.models import EscalationCase, Patient, Prescription
from cure_quest.services.google_workspace import credentials_from_tokens
from cure_quest.services.huggingface_medical import HuggingFaceMedicalService
from cure_quest.services.image_classifier import ImageClassifierService, CATEGORY_FOLDER_MAP

logger = logging.getLogger(__name__)


class IntegrationAgent:
    def __init__(self) -> None:
        self.drive = GoogleDriveAdapter()
        self.calendar = GoogleCalendarAdapter()
        self.gmail = GoogleGmailAdapter()
        self.analytics = BigQueryAnalyticsAdapter()
        self.openfda = OpenFDAAdapter()
        self.pharmacy = PharmacySearchAdapter()
        self.medical_memory = MedicalMemoryAdapter()
        self.huggingface_medical = HuggingFaceMedicalService()
        self.image_classifier = ImageClassifierService()
        self.speech = GoogleSpeechAdapter()

    def _with_retry(self, fn, *args, **kwargs):
        attempts = max(1, self.drive.settings.integration_max_retries + 1)
        delay_seconds = self.drive.settings.integration_retry_delay_ms / 1000.0
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                return fn(*args, **kwargs)
            except Exception as error:
                last_error = error
                if attempt == attempts - 1:
                    raise
                time.sleep(delay_seconds)
        raise last_error or RuntimeError("Unknown integration retry failure.")

    def _get_patient_google_credentials(self, db: Session, patient_id: int):
        patient = db.scalar(select(Patient).where(Patient.id == patient_id))
        if not patient or not patient.google_access_token:
            return None
        return credentials_from_tokens(
            access_token=patient.google_access_token,
            refresh_token=patient.google_refresh_token,
        )

    def upload_document(
        self,
        db: Session,
        patient_id: int,
        file_path: str,
        mime_type: str,
        prescription_id: int | None = None,
    ) -> dict:
        settings = self.drive.settings
        patient_credentials = self._get_patient_google_credentials(db, patient_id)

        # --- AI-powered image classification & subfolder routing ---
        image_category: str | None = None
        target_folder_id: str | None = None

        if settings.google_drive_classification_enabled and settings.google_drive_folder_id:
            image_category = self.image_classifier.classify_medical_image(file_path)
            subfolder_name = CATEGORY_FOLDER_MAP.get(image_category, "Other")
            logger.info(
                "Image classified as %s → routing to subfolder '%s'",
                image_category,
                subfolder_name,
            )
            try:
                target_folder_id = self._with_retry(
                    self.drive.get_or_create_subfolder,
                    parent_folder_id=settings.google_drive_folder_id,
                    folder_name=subfolder_name,
                    credentials=patient_credentials,
                )
            except Exception:
                logger.exception("Failed to resolve subfolder — uploading to root folder")
                target_folder_id = None

        result = self._with_retry(
            self.drive.upload_file,
            file_path=file_path,
            mime_type=mime_type,
            folder_id=target_folder_id,
            credentials=patient_credentials,
        )

        # Attach the classification result to the response.
        if image_category:
            result["image_category"] = image_category

        if prescription_id is not None:
            prescription = db.scalar(select(Prescription).where(Prescription.id == prescription_id))
            if prescription is not None:
                prescription.document_drive_file_id = result.get("id")
                prescription.document_drive_file_url = result.get("webViewLink")
                db.commit()
        return result

    def create_calendar_event(
        self,
        db: Session,
        patient_id: int,
        summary: str,
        minutes_from_now: int,
        duration_minutes: int,
        escalation_case_id: int | None = None,
    ) -> dict:
        patient_credentials = self._get_patient_google_credentials(db, patient_id)
        result = self._with_retry(
            self.calendar.create_demo_event,
            summary=summary,
            minutes_from_now=minutes_from_now,
            duration_minutes=duration_minutes,
            credentials=patient_credentials,
        )
        if escalation_case_id is not None:
            case = db.scalar(select(EscalationCase).where(EscalationCase.id == escalation_case_id))
            if case is not None:
                case.calendar_event_id = result.get("id")
                case.calendar_event_url = result.get("htmlLink")
                db.commit()
        return result

    def log_integration_event(self, event_type: str, payload: dict) -> dict:
        try:
            return self.analytics.log_event(event_type=event_type, payload=payload)
        except Exception as error:
            return {
                "logged": False,
                "event_id": None,
                "provider": "bigquery",
                "errors": [str(error)],
            }

    def lookup_drug_label(self, medication_name: str) -> dict:
        return self._with_retry(self.openfda.lookup_drug_label, medication_name)

    def list_drive_files(self, credentials=None, max_results: int = 5) -> list[dict]:
        try:
            return self._with_retry(
                self.drive.list_accessible_files,
                page_size=max_results,
                credentials=credentials,
            )
        except Exception as error:
            logger.error("Drive list failed: %s", error)
            return []

    def search_nearby_pharmacies(self, location_query: str) -> dict:
        return self._with_retry(self.pharmacy.search_nearby_pharmacies, location_query)

    def store_medical_memory(
        self,
        db: Session,
        patient_id: int,
        source_type: str,
        query_text: str | None = None,
        file_path: str | None = None,
        drive_file_id: str | None = None,
        drive_file_url: str | None = None,
        metadata: dict | None = None,
        use_live_embedding: bool = False,
    ) -> dict:
        content, modality = self.medical_memory.build_content_from_inputs(query_text=query_text, file_path=file_path)
        embedding_vector = None
        embedding_model = None
        if use_live_embedding and self.huggingface_medical.is_configured():
            if modality in {"image", "document"} and file_path:
                embedded = self.huggingface_medical.medsiglip_embed(image_path=file_path)
            else:
                embedded = self.huggingface_medical.medsiglip_embed(text=content)
            embedding_vector = embedded["embedding_vector"]
            embedding_model = embedded["model"]
        memory, synced = self.medical_memory.store_memory(
            db=db,
            patient_id=patient_id,
            source_type=source_type,
            modality=modality,
            content=content,
            source_reference=file_path,
            drive_file_id=drive_file_id,
            drive_file_url=drive_file_url,
            metadata=metadata,
            embedding_vector=embedding_vector,
            embedding_model=embedding_model,
        )
        return {
            "memory_id": memory.id,
            "patient_id": patient_id,
            "source_type": memory.source_type,
            "modality": memory.modality,
            "embedding_model": memory.embedding_model,
            "summary_text": memory.summary_text,
            "live_embedding_used": embedding_vector is not None,
            "vector_store_synced": synced,
        }

    def search_medical_memory(
        self,
        db: Session,
        patient_id: int,
        query_text: str,
        modality: str | None = None,
        limit: int = 5,
    ) -> dict:
        results = self.medical_memory.search_similar(
            db=db,
            patient_id=patient_id,
            query_text=query_text,
            modality=modality,
            limit=limit,
        )
        return {
            "patient_id": patient_id,
            "query_text": query_text,
            "results": results,
        }

    def run_medgemma(self, prompt: str, image_path: str | None = None, max_new_tokens: int = 128) -> dict:
        return self.huggingface_medical.medgemma_generate(
            prompt=prompt,
            image_path=image_path,
            max_new_tokens=max_new_tokens,
        )

    def run_medsiglip_classification(self, image_path: str, candidate_labels: list[str]) -> dict:
        return self.huggingface_medical.medsiglip_classify(
            image_path=image_path,
            candidate_labels=candidate_labels,
        )

    def transcribe_audio(self, audio_bytes: bytes) -> dict:
        try:
            transcript = self._with_retry(self.speech.transcribe_audio, audio_bytes=audio_bytes)
            return {"transcript": transcript, "error": None}
        except Exception as error:
            logger.error("Audio transcription failed: %s", error)
            return {"transcript": None, "error": str(error)}

    def synthesize_speech(self, text: str) -> dict:
        try:
            audio_bytes = self._with_retry(self.speech.synthesize_speech, text=text)
            return {"audio_bytes": audio_bytes, "error": None}
        except Exception as error:
            logger.error("Speech synthesis failed: %s", error)
            return {"audio_bytes": None, "error": str(error)}

    def ensure_bigquery_table(self) -> dict:
        return self.analytics.ensure_table()

    def list_health_emails(self, credentials=None, max_results: int = 5) -> list[dict]:
        try:
            return self._with_retry(
                self.gmail.list_recent_health_emails,
                credentials=credentials,
                max_results=max_results,
            )
        except Exception as error:
            logger.error("Gmail list failed: %s", error)
            return []

    def send_care_email(self, to: str, subject: str, body_html: str, credentials=None) -> dict:
        try:
            return self._with_retry(
                self.gmail.send_care_summary,
                to=to,
                subject=subject,
                body_html=body_html,
                credentials=credentials,
            )
        except Exception as error:
            logger.error("Gmail send failed: %s", error)
            return {"sent": False, "message_id": None, "error": str(error)}
