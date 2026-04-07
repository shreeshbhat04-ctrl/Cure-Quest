from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cure_quest.db.session import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    preferred_language: Mapped[str] = mapped_column(String(50), default="en")
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    conditions: Mapped[list["ChronicCondition"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class ChronicCondition(Base):
    __tablename__ = "chronic_conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    name: Mapped[str] = mapped_column(String(255))
    condition_type: Mapped[str] = mapped_column(String(32), default="chronic")
    last_updated: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped[Patient] = relationship(back_populates="conditions")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    medication_name: Mapped[str] = mapped_column(String(255))
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    review_status: Mapped[str] = mapped_column(String(50), default="pending")
    document_drive_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_drive_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient: Mapped[Patient] = relationship(back_populates="prescriptions")


class MedicationEvent(Base):
    __tablename__ = "medication_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    medication_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EscalationCase(Base):
    __tablename__ = "escalation_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    case_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="open")
    summary: Mapped[str] = mapped_column(Text)
    external_ticket_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_ticket_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    drive_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drive_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calendar_event_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    pharmacy_search_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    channel: Mapped[str] = mapped_column(String(50))
    message_type: Mapped[str] = mapped_column(String(50))
    body: Mapped[str] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(String(50), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient: Mapped[Patient] = relationship(back_populates="notifications")


class MedicalMemory(Base):
    __tablename__ = "medical_memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    source_type: Mapped[str] = mapped_column(String(50))
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modality: Mapped[str] = mapped_column(String(32), default="text")
    embedding_model: Mapped[str] = mapped_column(String(128))
    embedding_vector: Mapped[str] = mapped_column(Text)
    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    drive_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drive_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
