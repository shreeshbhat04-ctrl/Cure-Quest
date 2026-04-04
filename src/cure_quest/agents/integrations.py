from sqlalchemy import select
from sqlalchemy.orm import Session
import time

from cure_quest.adapters.analytics import BigQueryAnalyticsAdapter
from cure_quest.adapters.calendar import GoogleCalendarAdapter
from cure_quest.adapters.drive import GoogleDriveAdapter
from cure_quest.adapters.medical_memory import MedicalMemoryAdapter
from cure_quest.adapters.openfda import OpenFDAAdapter
from cure_quest.adapters.pharmacy import PharmacySearchAdapter
from cure_quest.db.models import EscalationCase, Prescription
from cure_quest.services.huggingface_medical import HuggingFaceMedicalService


class IntegrationAgent:
    def __init__(self) -> None:
        self.drive = GoogleDriveAdapter()
        self.calendar = GoogleCalendarAdapter()
        self.analytics = BigQueryAnalyticsAdapter()
        self.openfda = OpenFDAAdapter()
        self.pharmacy = PharmacySearchAdapter()
        self.medical_memory = MedicalMemoryAdapter()
        self.huggingface_medical = HuggingFaceMedicalService()

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

    def upload_document(
        self,
        db: Session,
        patient_id: int,
        file_path: str,
        mime_type: str,
        prescription_id: int | None = None,
    ) -> dict:
        _ = patient_id
        result = self._with_retry(self.drive.upload_file, file_path=file_path, mime_type=mime_type)
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
        _ = patient_id
        result = self._with_retry(
            self.calendar.create_demo_event,
            summary=summary,
            minutes_from_now=minutes_from_now,
            duration_minutes=duration_minutes,
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

    def ensure_bigquery_table(self) -> dict:
        return self.analytics.ensure_table()
