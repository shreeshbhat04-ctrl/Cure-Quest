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
    document_file_path: str | None = None
    calendar_summary: str | None = None
    create_calendar_event: bool = False
    calendar_minutes_from_now: int = 30
    calendar_duration_minutes: int = 30
    pharmacy_location_query: str | None = None


class EscalateResponse(BaseModel):
    case_id: int
    external_ticket_id: str | None
    status: str
    external_ticket_url: str | None = None
    drive_file_id: str | None = None
    drive_file_url: str | None = None
    calendar_event_id: str | None = None
    calendar_event_url: str | None = None
    pharmacy_search_summary: str | None = None


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
    external_ticket_url: str | None = None
    drive_file_id: str | None = None
    drive_file_url: str | None = None
    calendar_event_id: str | None = None
    calendar_event_url: str | None = None
    pharmacy_search_summary: str | None = None


class DriveUploadRequest(BaseModel):
    patient_id: int
    file_path: str
    mime_type: str = "application/octet-stream"
    prescription_id: int | None = None


class DriveUploadResponse(BaseModel):
    patient_id: int
    file_id: str
    file_name: str
    web_view_link: str | None = None
    prescription_id: int | None = None
    image_category: str | None = None


class CalendarEventRequest(BaseModel):
    patient_id: int
    summary: str
    minutes_from_now: int = 30
    duration_minutes: int = 30
    escalation_case_id: int | None = None


class CalendarEventResponse(BaseModel):
    patient_id: int
    event_id: str
    html_link: str | None = None
    escalation_case_id: int | None = None


class DrugLabelRequest(BaseModel):
    medication_name: str


class DrugLabelResponse(BaseModel):
    medication_name: str
    found: bool
    label: dict | None = None


class PharmacySearchRequest(BaseModel):
    location_query: str


class PharmacySearchResponse(BaseModel):
    provider: str
    pharmacies: list[dict]


class RoutineTaskResponse(BaseModel):
    task_id: str
    name: str
    completed: bool
    due_on: str | None = None
    notes: str | None = None
    assignee_name: str | None = None
    permalink_url: str | None = None


class DailyCheckInResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    conditions: list[dict]
    routine_tasks: list[RoutineTaskResponse]
    message: str


class HitlReportRequest(BaseModel):
    patient_id: int
    context_summary: str | None = None
    create_case: bool = False
    case_type: str = "doctor_review"


class HitlReportResponse(BaseModel):
    patient_id: int
    report: str
    case_id: int | None = None
    external_ticket_id: str | None = None
    external_ticket_url: str | None = None


class RoutineSnapshotResponse(BaseModel):
    patient_id: int
    tasks: list[RoutineTaskResponse]


class DietSupportRequest(BaseModel):
    patient_id: int
    medication_name: str | None = None
    location_query: str | None = None


class DietSupportResponse(BaseModel):
    patient_id: int
    conditions: list[dict]
    diet_plan: dict
    pharmacy_result: dict


class DocumentPipelineRequest(BaseModel):
    patient_id: int
    file_path: str
    raw_text_hint: str | None = None
    prescription_id: int | None = None


class DocumentPipelineResponse(BaseModel):
    patient_id: int
    file_name: str
    file_path: str
    prescription_id: int | None = None
    ocr_model: str
    reasoning_model: str
    support_model: str | None = None
    storage_target: str
    ocr_strategy: str
    raw_text_hint: str | None = None
    route_type: str
    route_reason: str
    execution_plan: list[str]


class ConversationRoutingRequest(BaseModel):
    patient_id: int
    message: str


class ConversationRoutingResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    message: str
    route_type: str
    primary_model: str
    support_model: str | None = None
    reason: str
    suggested_response_style: str
    execution_plan: list[str]


class MedicalRoutingRequest(BaseModel):
    patient_id: int
    query_text: str | None = None
    file_path: str | None = None


class MedicalRoutingResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    query_text: str | None = None
    file_path: str | None = None
    route_type: str
    primary_model: str
    secondary_model: str | None = None
    support_model: str | None = None
    reason: str
    execution_plan: list[str]


class MedicalMemoryStoreRequest(BaseModel):
    patient_id: int
    source_type: str = "manual_upload"
    query_text: str | None = None
    file_path: str | None = None
    drive_file_id: str | None = None
    drive_file_url: str | None = None
    use_live_embedding: bool = False
    metadata: dict = Field(default_factory=dict)


class MedicalMemoryStoreResponse(BaseModel):
    memory_id: int
    patient_id: int
    source_type: str
    modality: str
    embedding_model: str
    summary_text: str | None = None
    live_embedding_used: bool
    route_type: str
    route_reason: str


class MedicalMemorySearchRequest(BaseModel):
    patient_id: int
    query_text: str
    modality: str | None = None
    limit: int = 5


class MedicalMemorySearchResult(BaseModel):
    memory_id: int
    source_type: str
    source_reference: str | None = None
    modality: str
    embedding_model: str
    summary_text: str | None = None
    drive_file_id: str | None = None
    drive_file_url: str | None = None
    metadata: dict
    similarity: float


class MedicalMemorySearchResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    query_text: str
    results: list[MedicalMemorySearchResult]


class MedGemmaRequest(BaseModel):
    patient_id: int
    prompt: str
    image_path: str | None = None
    max_new_tokens: int = 128


class MedGemmaResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    provider: str
    model: str
    prompt: str
    image_path: str | None = None
    result: list | dict


class MedSigLIPClassificationRequest(BaseModel):
    patient_id: int
    image_path: str
    candidate_labels: list[str]


class MedSigLIPClassificationResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    provider: str
    model: str
    image_path: str
    candidate_labels: list[str]
    result: list | dict


class DocumentFlowRequest(BaseModel):
    patient_id: int
    image_reference: str | None = None
    raw_text_hint: str | None = None
    document_file_path: str | None = None
    pharmacy_location_query: str | None = None
    create_calendar_event: bool = True


class DocumentFlowResponse(BaseModel):
    patient_id: int
    prescription: dict
    document_pipeline: dict
    drive_result: dict | None = None
    memory_result: dict
    alternatives: list[dict]
    diet_support: dict
    pharmacy_result: dict | None = None
    escalation_required: bool
    safety_summary: str
    case: dict | None = None
    calendar_result: dict | None = None
    notification: dict
    flow_notes: list[str]


class RoutineAutomationResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    routine_tasks: list[RoutineTaskResponse]
    routine_summary: str
    risk_level: str
    overdue_count: int
    due_today_count: int
    message: str
    case: dict | None = None


class OrchestrationManifestResponse(BaseModel):
    patient_id: int
    profile: dict | None = None
    conditions: list[dict]
    routine_tasks: list[RoutineTaskResponse]
    agent_manifest: dict
    trigger_manifest: dict
