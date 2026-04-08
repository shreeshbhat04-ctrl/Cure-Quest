from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from cure_quest.agents.orchestrator import Orchestrator
from cure_quest.api.models import (
    CaseResponse,
    CalendarEventRequest,
    CalendarEventResponse,
    CheckAlternativesRequest,
    CheckAlternativesResponse,
    ConversationRoutingRequest,
    ConversationRoutingResponse,
    DailyCheckInResponse,
    DietSupportRequest,
    DietSupportResponse,
    DocumentFlowRequest,
    DocumentFlowResponse,
    DocumentPipelineRequest,
    DocumentPipelineResponse,
    DriveUploadRequest,
    DriveUploadResponse,
    DrugLabelRequest,
    DrugLabelResponse,
    EscalateRequest,
    EscalateResponse,
    HitlReportRequest,
    HitlReportResponse,
    MedicalRoutingRequest,
    MedicalRoutingResponse,
    MedicalMemorySearchRequest,
    MedicalMemorySearchResponse,
    MedicalMemoryStoreRequest,
    MedicalMemoryStoreResponse,
    MedGemmaRequest,
    MedGemmaResponse,
    MedSigLIPClassificationRequest,
    MedSigLIPClassificationResponse,
    NotifyRequest,
    NotifyResponse,
    OrchestrationManifestResponse,
    PatientIntakeRequest,
    PatientIntakeResponse,
    PharmacySearchRequest,
    PharmacySearchResponse,
    PrescriptionScanRequest,
    PrescriptionScanResponse,
    RoutineSnapshotResponse,
    RoutineAutomationResponse,
)
from cure_quest.db.models import EscalationCase
from cure_quest.db.models import ChronicCondition, MedicalMemory, Notification, Patient, Prescription
from cure_quest.db.session import get_db

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/auth/google")
def google_auth_exchange(
    code: str = Form(...),
    db: Session = Depends(get_db),
):
    """Exchange a Google authorization code for tokens, match to a patient."""
    import google_auth_oauthlib.flow as oauthflow
    from cure_quest.config import get_settings

    settings = get_settings()
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        raise HTTPException(status_code=500, detail="OAuth client not configured on server.")

    # Build client config for web application flow
    client_config = {
        "web": {
            "client_id": settings.google_oauth_client_id,
            "client_secret": settings.google_oauth_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["postmessage"],
        }
    }
    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ]
    flow = oauthflow.Flow.from_client_config(client_config, scopes=scopes)
    flow.redirect_uri = "postmessage"

    try:
        flow.fetch_token(code=code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {e}")

    creds = flow.credentials
    # Extract user info from ID token
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    try:
        id_info = id_token.verify_oauth2_token(
            creds.id_token, google_requests.Request(), settings.google_oauth_client_id
        )
        user_email = id_info.get("email", "")
        user_name = id_info.get("name", "")
    except Exception:
        user_email = ""
        user_name = ""

    # Try to match to existing patient by email, or by ID 2 as fallback
    patient = None
    if user_email:
        patient = db.scalar(select(Patient).where(Patient.google_email == user_email))
    if patient is None:
        # Fallback: assign to patient 2 (Shreesha) and set their email
        patient = db.scalar(select(Patient).where(Patient.id == 2))
        if patient is None:
            raise HTTPException(status_code=404, detail="No matching patient found.")
        patient.google_email = user_email

    # Save tokens
    patient.google_access_token = creds.token
    patient.google_refresh_token = creds.refresh_token
    patient.google_token_expiry = creds.expiry
    db.commit()

    return {
        "patient_id": patient.id,
        "name": patient.full_name,
        "email": user_email or patient.google_email,
        "google_connected": True,
    }


@router.get("/auth/google/status/{patient_id}")
def google_auth_status(patient_id: int, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.id == patient_id))
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    has_tokens = bool(patient.google_access_token)
    return {
        "patient_id": patient_id,
        "google_connected": has_tokens,
        "email": patient.google_email,
        "services": {
            "drive": has_tokens,
            "calendar": has_tokens,
            "gmail": has_tokens,
        },
    }


@router.get("/gmail/{patient_id}/health-emails")
def list_gmail_health_emails(patient_id: int, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.id == patient_id))
    if not patient or not patient.google_access_token:
        return {"patient_id": patient_id, "emails": [], "error": "Gmail not connected."}

    from cure_quest.services.google_workspace import credentials_from_tokens
    creds = credentials_from_tokens(
        access_token=patient.google_access_token,
        refresh_token=patient.google_refresh_token,
    )
    emails = orchestrator.integrations.list_health_emails(credentials=creds, max_results=5)
    return {"patient_id": patient_id, "emails": emails}


@router.post("/gmail/send-care-summary")
def send_gmail_care_summary(
    patient_id: int = Form(...),
    to_email: str = Form(...),
    subject: str = Form(...),
    body_html: str = Form(...),
    db: Session = Depends(get_db),
):
    patient = db.scalar(select(Patient).where(Patient.id == patient_id))
    if not patient or not patient.google_access_token:
        raise HTTPException(status_code=400, detail="Gmail not connected for this patient.")

    from cure_quest.services.google_workspace import credentials_from_tokens
    creds = credentials_from_tokens(
        access_token=patient.google_access_token,
        refresh_token=patient.google_refresh_token,
    )
    result = orchestrator.integrations.send_care_email(
        to=to_email,
        subject=subject,
        body_html=body_html,
        credentials=creds,
    )
    return {"patient_id": patient_id, **result}



@router.get("/demo/patient/{patient_id}/workspace")
def patient_workspace(patient_id: int, db: Session = Depends(get_db)) -> dict:
    patient = db.scalar(select(Patient).where(Patient.id == patient_id))
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    conditions = db.scalars(
        select(ChronicCondition).where(ChronicCondition.patient_id == patient_id).order_by(ChronicCondition.id.desc())
    ).all()
    prescriptions = db.scalars(
        select(Prescription).where(Prescription.patient_id == patient_id).order_by(Prescription.created_at.desc())
    ).all()
    notifications = db.scalars(
        select(Notification).where(Notification.patient_id == patient_id).order_by(Notification.created_at.desc())
    ).all()
    cases = db.scalars(
        select(EscalationCase).where(EscalationCase.patient_id == patient_id).order_by(EscalationCase.created_at.desc())
    ).all()
    memories = db.scalars(
        select(MedicalMemory).where(MedicalMemory.patient_id == patient_id).order_by(MedicalMemory.created_at.desc())
    ).all()

    checkin = orchestrator.build_daily_checkin(patient_id)
    manifest = orchestrator.get_orchestration_manifest(patient_id)

    return {
        "patient": {
            "id": patient.id,
            "full_name": patient.full_name,
            "preferred_language": patient.preferred_language,
            "summary": patient.summary,
            "date_of_birth": None if patient.date_of_birth is None else patient.date_of_birth.isoformat(),
        },
        "conditions": [
            {
                "id": item.id,
                "name": item.name,
                "condition_type": item.condition_type,
                "last_updated": None if item.last_updated is None else item.last_updated.isoformat(),
                "notes": item.notes,
            }
            for item in conditions
        ],
        "prescriptions": [
            {
                "id": item.id,
                "medication_name": item.medication_name,
                "dosage": item.dosage,
                "instructions": item.instructions,
                "review_status": item.review_status,
                "confidence_score": item.confidence_score,
                "document_drive_file_url": item.document_drive_file_url,
                "created_at": item.created_at.isoformat(),
            }
            for item in prescriptions
        ],
        "notifications": [
            {
                "id": item.id,
                "channel": item.channel,
                "message_type": item.message_type,
                "body": item.body,
                "delivery_status": item.delivery_status,
                "created_at": item.created_at.isoformat(),
            }
            for item in notifications
        ],
        "cases": [
            {
                "id": item.id,
                "case_type": item.case_type,
                "status": item.status,
                "summary": item.summary,
                "external_ticket_id": item.external_ticket_id,
                "external_ticket_url": item.external_ticket_url,
                "drive_file_url": item.drive_file_url,
                "calendar_event_url": item.calendar_event_url,
                "pharmacy_search_summary": item.pharmacy_search_summary,
                "created_at": item.created_at.isoformat(),
            }
            for item in cases
        ],
        "memories": [
            {
                "id": item.id,
                "source_type": item.source_type,
                "modality": item.modality,
                "embedding_model": item.embedding_model,
                "summary_text": item.summary_text,
                "drive_file_url": item.drive_file_url,
                "created_at": item.created_at.isoformat(),
            }
            for item in memories
        ],
        "checkin": checkin,
        "manifest": manifest,
    }


@router.post("/patient/intake", response_model=PatientIntakeResponse)
def patient_intake(payload: PatientIntakeRequest, db: Session = Depends(get_db)) -> PatientIntakeResponse:
    patient = orchestrator.intake.intake_patient(db, payload)
    return PatientIntakeResponse(patient_id=patient.id, summary=patient.summary or "")


@router.post("/prescription/scan", response_model=PrescriptionScanResponse)
def prescription_scan(payload: PrescriptionScanRequest, db: Session = Depends(get_db)) -> PrescriptionScanResponse:
    prescription = orchestrator.intake.scan_prescription(
        db=db,
        patient_id=payload.patient_id,
        image_reference=payload.image_reference,
        raw_text_hint=payload.raw_text_hint,
    )
    return PrescriptionScanResponse(
        prescription_id=prescription.id,
        medication_name=prescription.medication_name,
        dosage=prescription.dosage,
        instructions=prescription.instructions,
        confidence_score=prescription.confidence_score,
        review_status=prescription.review_status,
    )


@router.post("/patient/check-alternatives", response_model=CheckAlternativesResponse)
def check_alternatives(payload: CheckAlternativesRequest) -> CheckAlternativesResponse:
    candidates, escalation_required, safety_summary = orchestrator.evaluate_alternatives(
        patient_id=payload.patient_id,
        unavailable_medication=payload.unavailable_medication,
    )
    return CheckAlternativesResponse(
        patient_id=payload.patient_id,
        candidates=candidates,
        escalation_required=escalation_required,
        safety_summary=safety_summary,
    )


@router.post("/patient/escalate", response_model=EscalateResponse)
def escalate(payload: EscalateRequest, db: Session = Depends(get_db)) -> EscalateResponse:
    case = orchestrator.hitl.create_case(db, payload.patient_id, payload.case_type, payload.summary)
    drive_result = None
    if payload.document_file_path:
        drive_result = orchestrator.integrations.upload_document(
            db=db,
            patient_id=payload.patient_id,
            file_path=payload.document_file_path,
            mime_type="application/pdf" if payload.document_file_path.lower().endswith(".pdf") else "application/octet-stream",
        )
        case.drive_file_id = drive_result.get("id")
        case.drive_file_url = drive_result.get("webViewLink")

    calendar_result = None
    if payload.create_calendar_event:
        calendar_result = orchestrator.integrations.create_calendar_event(
            db=db,
            patient_id=payload.patient_id,
            summary=payload.calendar_summary or f"Cure-Quest follow-up for patient {payload.patient_id}",
            minutes_from_now=payload.calendar_minutes_from_now,
            duration_minutes=payload.calendar_duration_minutes,
            escalation_case_id=case.id,
        )

    pharmacy_result = None
    if payload.pharmacy_location_query:
        pharmacy_result = orchestrator.integrations.search_nearby_pharmacies(payload.pharmacy_location_query)
        pharmacy_names = [item["name"] for item in pharmacy_result.get("pharmacies", [])[:3] if item.get("name")]
        case.pharmacy_search_summary = ", ".join(pharmacy_names) if pharmacy_names else "No pharmacies found"

    db.add(case)
    db.commit()
    db.refresh(case)

    orchestrator.integrations.log_integration_event(
        "escalation_case_created",
        {
            "case_id": case.id,
            "patient_id": payload.patient_id,
            "external_ticket_id": case.external_ticket_id,
            "drive_file_id": case.drive_file_id,
            "calendar_event_id": case.calendar_event_id,
            "pharmacy_search_summary": case.pharmacy_search_summary,
        },
    )

    return EscalateResponse(
        case_id=case.id,
        external_ticket_id=case.external_ticket_id,
        status=case.status,
        external_ticket_url=case.external_ticket_url,
        drive_file_id=case.drive_file_id,
        drive_file_url=case.drive_file_url,
        calendar_event_id=case.calendar_event_id,
        calendar_event_url=case.calendar_event_url,
        pharmacy_search_summary=case.pharmacy_search_summary,
    )


@router.post("/patient/notify", response_model=NotifyResponse)
def notify(payload: NotifyRequest, db: Session = Depends(get_db)) -> NotifyResponse:
    notification = orchestrator.communications.notify(
        db,
        patient_id=payload.patient_id,
        channel=payload.channel,
        message_type=payload.message_type,
        message_body=payload.message_body,
    )
    return NotifyResponse(notification_id=notification.id, delivery_status=notification.delivery_status)


@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)) -> CaseResponse:
    case = db.scalar(select(EscalationCase).where(EscalationCase.id == case_id))
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseResponse(
        case_id=case.id,
        patient_id=case.patient_id,
        case_type=case.case_type,
        status=case.status,
        summary=case.summary,
        external_ticket_id=case.external_ticket_id,
        external_ticket_url=case.external_ticket_url,
        drive_file_id=case.drive_file_id,
        drive_file_url=case.drive_file_url,
        calendar_event_id=case.calendar_event_id,
        calendar_event_url=case.calendar_event_url,
        pharmacy_search_summary=case.pharmacy_search_summary,
    )


@router.post("/documents/upload", response_model=DriveUploadResponse)
def upload_document(payload: DriveUploadRequest, db: Session = Depends(get_db)) -> DriveUploadResponse:
    result = orchestrator.integrations.upload_document(
        db=db,
        patient_id=payload.patient_id,
        file_path=payload.file_path,
        mime_type=payload.mime_type,
        prescription_id=payload.prescription_id,
    )
    return DriveUploadResponse(
        patient_id=payload.patient_id,
        file_id=result["id"],
        file_name=result["name"],
        web_view_link=result.get("webViewLink"),
        prescription_id=payload.prescription_id,
        image_category=result.get("image_category"),
    )


@router.post("/documents/upload-file", response_model=DriveUploadResponse)
def upload_document_file(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    prescription_id: int | None = Form(None),
    db: Session = Depends(get_db),
) -> DriveUploadResponse:
    import tempfile, os
    suffix = os.path.splitext(file.filename or "upload")[1] or ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        result = orchestrator.integrations.upload_document(
            db=db,
            patient_id=patient_id,
            file_path=tmp_path,
            mime_type=file.content_type or "application/octet-stream",
            prescription_id=prescription_id,
        )
    finally:
        os.unlink(tmp_path)

    return DriveUploadResponse(
        patient_id=patient_id,
        file_id=result["id"],
        file_name=result["name"],
        web_view_link=result.get("webViewLink"),
        prescription_id=prescription_id,
        image_category=result.get("image_category"),
    )


@router.post("/calendar/events", response_model=CalendarEventResponse)
def create_calendar_event(payload: CalendarEventRequest, db: Session = Depends(get_db)) -> CalendarEventResponse:
    result = orchestrator.integrations.create_calendar_event(
        db=db,
        patient_id=payload.patient_id,
        summary=payload.summary,
        minutes_from_now=payload.minutes_from_now,
        duration_minutes=payload.duration_minutes,
        escalation_case_id=payload.escalation_case_id,
    )
    return CalendarEventResponse(
        patient_id=payload.patient_id,
        event_id=result["id"],
        html_link=result.get("htmlLink"),
        escalation_case_id=payload.escalation_case_id,
    )


@router.post("/drug/label", response_model=DrugLabelResponse)
def lookup_drug_label(payload: DrugLabelRequest) -> DrugLabelResponse:
    result = orchestrator.integrations.lookup_drug_label(payload.medication_name)
    return DrugLabelResponse(**result)


@router.post("/pharmacy/search", response_model=PharmacySearchResponse)
def pharmacy_search(payload: PharmacySearchRequest) -> PharmacySearchResponse:
    result = orchestrator.integrations.search_nearby_pharmacies(payload.location_query)
    return PharmacySearchResponse(**result)


@router.get("/orchestration/check-in/{patient_id}", response_model=DailyCheckInResponse)
def orchestration_checkin(patient_id: int) -> DailyCheckInResponse:
    result = orchestrator.build_daily_checkin(patient_id)
    return DailyCheckInResponse(
        patient_id=patient_id,
        profile=result["profile"],
        conditions=result["conditions"],
        routine_tasks=result["routine_tasks"],
        message=result["message"],
    )


@router.get("/orchestration/routine/{patient_id}", response_model=RoutineSnapshotResponse)
def orchestration_routine(patient_id: int) -> RoutineSnapshotResponse:
    _ = patient_id
    tasks = orchestrator.routine.get_daily_routine()
    return RoutineSnapshotResponse(patient_id=patient_id, tasks=[task.__dict__ for task in tasks])


@router.post("/orchestration/hitl-report", response_model=HitlReportResponse)
def orchestration_hitl_report(payload: HitlReportRequest, db: Session = Depends(get_db)) -> HitlReportResponse:
    report = orchestrator.hitl.build_detailed_report(db, payload.patient_id, payload.context_summary)
    case_id = None
    external_ticket_id = None
    external_ticket_url = None
    if payload.create_case:
        case = orchestrator.hitl.create_case(db, payload.patient_id, payload.case_type, report)
        case_id = case.id
        external_ticket_id = case.external_ticket_id
        external_ticket_url = case.external_ticket_url

    return HitlReportResponse(
        patient_id=payload.patient_id,
        report=report,
        case_id=case_id,
        external_ticket_id=external_ticket_id,
        external_ticket_url=external_ticket_url,
    )


@router.post("/orchestration/hitl-comprehension")
def orchestration_hitl_comprehension(payload: HitlReportRequest, db: Session = Depends(get_db)):
    result = orchestrator.hitl.build_ai_comprehension(db, payload.patient_id)
    return {"patient_id": payload.patient_id, **result}


@router.post("/patient/reminders")
def save_reminder(
    patient_id: int = Form(...),
    medication_name: str = Form(...),
    reminder_time: str = Form(...),
    db: Session = Depends(get_db),
):
    """Store a medication reminder. Using MedicationEvent as lightweight storage."""
    from cure_quest.db.models import MedicationEvent
    event = MedicationEvent(
        patient_id=patient_id,
        event_type="reminder_set",
        medication_name=medication_name,
        details=reminder_time,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {
        "id": event.id,
        "patient_id": patient_id,
        "medication_name": medication_name,
        "reminder_time": reminder_time,
        "status": "saved",
    }


@router.get("/patient/{patient_id}/reminders")
def get_reminders(patient_id: int, db: Session = Depends(get_db)):
    from cure_quest.db.models import MedicationEvent
    events = db.scalars(
        select(MedicationEvent)
        .where(MedicationEvent.patient_id == patient_id, MedicationEvent.event_type == "reminder_set")
        .order_by(MedicationEvent.created_at.desc())
    ).all()
    return {
        "patient_id": patient_id,
        "reminders": [
            {
                "id": e.id,
                "medication_name": e.medication_name,
                "reminder_time": e.details,
                "created_at": str(e.created_at),
            }
            for e in events
        ],
    }


@router.post("/orchestration/diet-support", response_model=DietSupportResponse)
def orchestration_diet_support(payload: DietSupportRequest) -> DietSupportResponse:
    result = orchestrator.build_diet_and_pharmacy_support(
        patient_id=payload.patient_id,
        medication_name=payload.medication_name,
        location_query=payload.location_query,
    )
    return DietSupportResponse(
        patient_id=payload.patient_id,
        conditions=result["conditions"],
        diet_plan=result["diet_plan"],
        pharmacy_result=result["pharmacy_result"],
    )


@router.post("/orchestration/document-pipeline", response_model=DocumentPipelineResponse)
def orchestration_document_pipeline(payload: DocumentPipelineRequest) -> DocumentPipelineResponse:
    result = orchestrator.build_document_pipeline(
        patient_id=payload.patient_id,
        file_path=payload.file_path,
        raw_text_hint=payload.raw_text_hint,
        prescription_id=payload.prescription_id,
    )
    return DocumentPipelineResponse(**result)


@router.post("/orchestration/run-document-flow", response_model=DocumentFlowResponse)
def orchestration_run_document_flow(payload: DocumentFlowRequest, db: Session = Depends(get_db)) -> DocumentFlowResponse:
    result = orchestrator.run_document_intake_flow(
        db=db,
        patient_id=payload.patient_id,
        image_reference=payload.image_reference,
        raw_text_hint=payload.raw_text_hint,
        document_file_path=payload.document_file_path,
        pharmacy_location_query=payload.pharmacy_location_query,
        create_calendar_event=payload.create_calendar_event,
    )
    return DocumentFlowResponse(**result)


@router.post("/orchestration/conversation-route", response_model=ConversationRoutingResponse)
def orchestration_conversation_route(payload: ConversationRoutingRequest, db: Session = Depends(get_db)) -> ConversationRoutingResponse:
    result = orchestrator.route_conversation(patient_id=payload.patient_id, message=payload.message, db=db)
    return ConversationRoutingResponse(**result)


import base64

@router.post("/orchestration/voice-route", response_model=ConversationRoutingResponse)
def orchestration_voice_route(
    patient_id: int = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ConversationRoutingResponse:
    audio_bytes = audio.file.read()
    stt_result = orchestrator.integrations.transcribe_audio(audio_bytes)
    
    transcript = stt_result.get("transcript")
    if not transcript:
        raise HTTPException(status_code=400, detail=f"Audio transcription failed: {stt_result.get('error')}")
        
    result = orchestrator.route_conversation(patient_id=patient_id, message=transcript, db=db)
    
    # Text-to-Speech logic for voice-route
    tts_result = orchestrator.integrations.synthesize_speech(result["message"])
    if tts_result.get("audio_bytes"):
        result["audio_base64"] = base64.b64encode(tts_result["audio_bytes"]).decode("utf-8")
        
    return ConversationRoutingResponse(**result)


@router.post("/orchestration/medical-route", response_model=MedicalRoutingResponse)
def orchestration_medical_route(payload: MedicalRoutingRequest) -> MedicalRoutingResponse:
    result = orchestrator.route_medical_input(
        patient_id=payload.patient_id,
        query_text=payload.query_text,
        file_path=payload.file_path,
    )
    return MedicalRoutingResponse(**result)


@router.post("/medical-memory/store", response_model=MedicalMemoryStoreResponse)
def medical_memory_store(payload: MedicalMemoryStoreRequest, db: Session = Depends(get_db)) -> MedicalMemoryStoreResponse:
    result = orchestrator.store_medical_memory(
        db=db,
        patient_id=payload.patient_id,
        source_type=payload.source_type,
        query_text=payload.query_text,
        file_path=payload.file_path,
        drive_file_id=payload.drive_file_id,
        drive_file_url=payload.drive_file_url,
        use_live_embedding=payload.use_live_embedding,
        metadata=payload.metadata,
    )
    return MedicalMemoryStoreResponse(**result)


@router.post("/medical-memory/search", response_model=MedicalMemorySearchResponse)
def medical_memory_search(payload: MedicalMemorySearchRequest, db: Session = Depends(get_db)) -> MedicalMemorySearchResponse:
    result = orchestrator.search_medical_memory(
        db=db,
        patient_id=payload.patient_id,
        query_text=payload.query_text,
        modality=payload.modality,
        limit=payload.limit,
    )
    return MedicalMemorySearchResponse(**result)


@router.get("/orchestration/routine-automation/{patient_id}", response_model=RoutineAutomationResponse)
def orchestration_routine_automation(patient_id: int, db: Session = Depends(get_db)) -> RoutineAutomationResponse:
    result = orchestrator.run_routine_automation(db=db, patient_id=patient_id)
    return RoutineAutomationResponse(**result)


@router.post("/medical-models/medgemma", response_model=MedGemmaResponse)
def medgemma_run(payload: MedGemmaRequest) -> MedGemmaResponse:
    result = orchestrator.run_medgemma(
        patient_id=payload.patient_id,
        prompt=payload.prompt,
        image_path=payload.image_path,
        max_new_tokens=payload.max_new_tokens,
    )
    return MedGemmaResponse(**result)


@router.post("/medical-models/medsiglip/classify", response_model=MedSigLIPClassificationResponse)
def medsiglip_classify(payload: MedSigLIPClassificationRequest) -> MedSigLIPClassificationResponse:
    result = orchestrator.run_medsiglip_classification(
        patient_id=payload.patient_id,
        image_path=payload.image_path,
        candidate_labels=payload.candidate_labels,
    )
    return MedSigLIPClassificationResponse(**result)


@router.get("/orchestration/manifest/{patient_id}", response_model=OrchestrationManifestResponse)
def orchestration_manifest(patient_id: int) -> OrchestrationManifestResponse:
    result = orchestrator.get_orchestration_manifest(patient_id)
    return OrchestrationManifestResponse(**result)
