from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from cure_quest.agents.orchestrator import Orchestrator
from cure_quest.api.models import (
    CaseResponse,
    CheckAlternativesRequest,
    CheckAlternativesResponse,
    EscalateRequest,
    EscalateResponse,
    NotifyRequest,
    NotifyResponse,
    PatientIntakeRequest,
    PatientIntakeResponse,
    PrescriptionScanRequest,
    PrescriptionScanResponse,
)
from cure_quest.db.models import EscalationCase
from cure_quest.db.session import get_db
from cure_quest.demo_ui.dashboard import render_dashboard

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/demo", response_class=HTMLResponse)
def demo() -> str:
    return render_dashboard()


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
    return EscalateResponse(case_id=case.id, external_ticket_id=case.external_ticket_id, status=case.status)


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
    )
