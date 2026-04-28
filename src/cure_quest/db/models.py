from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
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
    doctor_mappings: Mapped[list["PatientDoctorMap"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    profile_details: Mapped[list["PatientProfileDetail"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    vitals: Mapped[list["PatientVital"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    condition_snapshots: Mapped[list["PatientConditionSnapshot"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    asana_user_gid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    asana_workspace_gid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_image_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient_mappings: Mapped[list["PatientDoctorMap"]] = relationship(back_populates="doctor", cascade="all, delete-orphan")


class PatientDoctorMap(Base):
    __tablename__ = "patient_doctor_map"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))
    relationship_type: Mapped[str] = mapped_column(String(50), default="primary")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient: Mapped[Patient] = relationship(back_populates="doctor_mappings")
    doctor: Mapped[Doctor] = relationship(back_populates="patient_mappings")


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
    drive_path: Mapped[str | None] = mapped_column(Text, nullable=True)
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


class PatientProfileDetail(Base):
    __tablename__ = "patient_profile_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), unique=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(20), nullable=True)
    allergies_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    primary_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    patient: Mapped[Patient] = relationship(back_populates="profile_details")


class PatientVital(Base):
    __tablename__ = "patient_vitals"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    blood_pressure: Mapped[str | None] = mapped_column(String(50), nullable=True)
    heart_rate_bpm: Mapped[int | None] = mapped_column(nullable=True)
    blood_glucose_mg_dl: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient: Mapped[Patient] = relationship(back_populates="vitals")


class PatientConditionSnapshot(Base):
    __tablename__ = "patient_condition_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    snapshot_type: Mapped[str] = mapped_column(String(80), default="profile_update")
    summary: Mapped[str] = mapped_column(Text)
    profile_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    prescriptions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    vitals_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_event_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_event_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient: Mapped[Patient] = relationship(back_populates="condition_snapshots")


class EscalationCase(Base):
    __tablename__ = "escalation_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    case_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="open")
    summary: Mapped[str] = mapped_column(Text)
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("doctors.id"), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doctor_asana_gid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_ticket_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_ticket_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    drive_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drive_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calendar_event_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    pharmacy_search_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    drive_path: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    drive_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PendingAction(Base):
    __tablename__ = "pending_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    action_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="draft")
    draft_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_option_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))
    subject: Mapped[str] = mapped_column(String(500), default="General consultation")
    status: Mapped[str] = mapped_column(String(40), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="thread", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("chat_threads.id"))
    sender_role: Mapped[str] = mapped_column(String(40))
    sender_display_name: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    thread: Mapped[ChatThread] = relationship(back_populates="messages")


class SavedDietRecipe(Base):
    __tablename__ = "saved_diet_recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    recipe_id: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
