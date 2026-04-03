from datetime import date

from pydantic import BaseModel, Field


class ConditionInput(BaseModel):
    name: str
    condition_type: str = "chronic"
    last_updated: date | None = None
    notes: str | None = None


class PatientIntakeRequest(BaseModel):
    full_name: str
    preferred_language: str = "en"
    date_of_birth: date | None = None
    active_conditions: list[ConditionInput] = Field(default_factory=list)


class PatientIntakeResponse(BaseModel):
    patient_id: int
    summary: str


class PrescriptionScanRequest(BaseModel):
    patient_id: int
    image_reference: str | None = None
    raw_text_hint: str | None = None


class PrescriptionScanResponse(BaseModel):
    prescription_id: int
    medication_name: str
    dosage: str | None = None
    instructions: str | None = None
    confidence_score: float
    review_status: str


class CheckAlternativesRequest(BaseModel):
    patient_id: int
    unavailable_medication: str


class AlternativeCandidate(BaseModel):
    name: str
    formulation_note: str
    stock_status: str
    safety_note: str


class CheckAlternativesResponse(BaseModel):
    patient_id: int
    candidates: list[AlternativeCandidate]
    escalation_required: bool
    safety_summary: str


class EscalateRequest(BaseModel):
    patient_id: int
    case_type: str = "doctor_review"
    summary: str


class EscalateResponse(BaseModel):
    case_id: int
    external_ticket_id: str | None
    status: str


class NotifyRequest(BaseModel):
    patient_id: int
    message_type: str
    message_body: str
    channel: str = "mock_email"


class NotifyResponse(BaseModel):
    notification_id: int
    delivery_status: str


class CaseResponse(BaseModel):
    case_id: int
    patient_id: int
    case_type: str
    status: str
    summary: str
    external_ticket_id: str | None = None
