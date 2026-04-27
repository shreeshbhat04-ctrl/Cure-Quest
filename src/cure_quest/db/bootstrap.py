from sqlalchemy import inspect, text

from cure_quest.config import get_settings
from cure_quest.db.session import Base, engine
import cure_quest.db.models  # noqa


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
    _apply_lightweight_migrations()


def _apply_lightweight_migrations() -> None:
    settings = get_settings()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    expected_columns = {
        "patient_profile_details": {
            "height_cm": "ALTER TABLE patient_profile_details ADD COLUMN height_cm FLOAT",
            "weight_kg": "ALTER TABLE patient_profile_details ADD COLUMN weight_kg FLOAT",
            "blood_group": "ALTER TABLE patient_profile_details ADD COLUMN blood_group VARCHAR(20)",
            "allergies_json": "ALTER TABLE patient_profile_details ADD COLUMN allergies_json TEXT",
            "emergency_contact_name": "ALTER TABLE patient_profile_details ADD COLUMN emergency_contact_name VARCHAR(255)",
            "emergency_contact_phone": "ALTER TABLE patient_profile_details ADD COLUMN emergency_contact_phone VARCHAR(50)",
            "primary_language": "ALTER TABLE patient_profile_details ADD COLUMN primary_language VARCHAR(50)",
            "notes": "ALTER TABLE patient_profile_details ADD COLUMN notes TEXT",
            "updated_at": "ALTER TABLE patient_profile_details ADD COLUMN updated_at TIMESTAMP",
        },
        "patient_vitals": {
            "blood_pressure": "ALTER TABLE patient_vitals ADD COLUMN blood_pressure VARCHAR(50)",
            "heart_rate_bpm": "ALTER TABLE patient_vitals ADD COLUMN heart_rate_bpm INTEGER",
            "blood_glucose_mg_dl": "ALTER TABLE patient_vitals ADD COLUMN blood_glucose_mg_dl FLOAT",
            "temperature_c": "ALTER TABLE patient_vitals ADD COLUMN temperature_c FLOAT",
            "weight_kg": "ALTER TABLE patient_vitals ADD COLUMN weight_kg FLOAT",
            "source": "ALTER TABLE patient_vitals ADD COLUMN source VARCHAR(80)",
            "recorded_at": "ALTER TABLE patient_vitals ADD COLUMN recorded_at TIMESTAMP",
        },
        "patient_condition_snapshots": {
            "snapshot_type": "ALTER TABLE patient_condition_snapshots ADD COLUMN snapshot_type VARCHAR(80)",
            "summary": "ALTER TABLE patient_condition_snapshots ADD COLUMN summary TEXT",
            "profile_json": "ALTER TABLE patient_condition_snapshots ADD COLUMN profile_json TEXT",
            "conditions_json": "ALTER TABLE patient_condition_snapshots ADD COLUMN conditions_json TEXT",
            "prescriptions_json": "ALTER TABLE patient_condition_snapshots ADD COLUMN prescriptions_json TEXT",
            "vitals_json": "ALTER TABLE patient_condition_snapshots ADD COLUMN vitals_json TEXT",
            "source_event_type": "ALTER TABLE patient_condition_snapshots ADD COLUMN source_event_type VARCHAR(80)",
            "source_event_id": "ALTER TABLE patient_condition_snapshots ADD COLUMN source_event_id VARCHAR(80)",
            "created_at": "ALTER TABLE patient_condition_snapshots ADD COLUMN created_at TIMESTAMP",
        },
        "prescriptions": {
            "document_drive_file_id": "ALTER TABLE prescriptions ADD COLUMN document_drive_file_id VARCHAR(255)",
            "document_drive_file_url": "ALTER TABLE prescriptions ADD COLUMN document_drive_file_url TEXT",
            "drive_path": "ALTER TABLE prescriptions ADD COLUMN drive_path TEXT",
        },
        "escalation_cases": {
            "doctor_id": "ALTER TABLE escalation_cases ADD COLUMN doctor_id INTEGER",
            "doctor_name": "ALTER TABLE escalation_cases ADD COLUMN doctor_name VARCHAR(255)",
            "doctor_email": "ALTER TABLE escalation_cases ADD COLUMN doctor_email VARCHAR(255)",
            "doctor_asana_gid": "ALTER TABLE escalation_cases ADD COLUMN doctor_asana_gid VARCHAR(255)",
            "urgency": "ALTER TABLE escalation_cases ADD COLUMN urgency VARCHAR(50)",
            "external_ticket_url": "ALTER TABLE escalation_cases ADD COLUMN external_ticket_url TEXT",
            "drive_file_id": "ALTER TABLE escalation_cases ADD COLUMN drive_file_id VARCHAR(255)",
            "drive_file_url": "ALTER TABLE escalation_cases ADD COLUMN drive_file_url TEXT",
            "calendar_event_id": "ALTER TABLE escalation_cases ADD COLUMN calendar_event_id VARCHAR(255)",
            "calendar_event_url": "ALTER TABLE escalation_cases ADD COLUMN calendar_event_url TEXT",
            "pharmacy_search_summary": "ALTER TABLE escalation_cases ADD COLUMN pharmacy_search_summary TEXT",
            "drive_path": "ALTER TABLE escalation_cases ADD COLUMN drive_path TEXT",
        },
        "medical_memories": {
            "drive_path": "ALTER TABLE medical_memories ADD COLUMN drive_path TEXT",
        },
        "chat_threads": {
            "patient_id": "ALTER TABLE chat_threads ADD COLUMN patient_id INTEGER",
            "doctor_id": "ALTER TABLE chat_threads ADD COLUMN doctor_id INTEGER",
            "subject": "ALTER TABLE chat_threads ADD COLUMN subject VARCHAR(500)",
            "status": "ALTER TABLE chat_threads ADD COLUMN status VARCHAR(40)",
            "updated_at": "ALTER TABLE chat_threads ADD COLUMN updated_at TIMESTAMP",
        },
        "chat_messages": {
            "thread_id": "ALTER TABLE chat_messages ADD COLUMN thread_id INTEGER",
            "sender_role": "ALTER TABLE chat_messages ADD COLUMN sender_role VARCHAR(40)",
            "sender_display_name": "ALTER TABLE chat_messages ADD COLUMN sender_display_name VARCHAR(255)",
            "body": "ALTER TABLE chat_messages ADD COLUMN body TEXT",
        },
    }

    with engine.begin() as connection:
        if engine.dialect.name == "postgresql":
            try:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                connection.execute(
                    text(
                        f"""
                        CREATE TABLE IF NOT EXISTS {settings.medical_vector_table_name} (
                            memory_id BIGINT PRIMARY KEY REFERENCES medical_memories(id) ON DELETE CASCADE,
                            patient_id BIGINT NOT NULL,
                            source_type TEXT NOT NULL,
                            modality VARCHAR(32) NOT NULL,
                            embedding_model VARCHAR(128) NOT NULL,
                            embedding vector({settings.medical_embedding_dimensions}) NOT NULL,
                            summary_text TEXT,
                            created_at TIMESTAMPTZ DEFAULT NOW()
                        )
                        """
                    )
                )
                connection.execute(
                    text(
                        f"""
                        CREATE INDEX IF NOT EXISTS idx_{settings.medical_vector_table_name}_patient_id
                        ON {settings.medical_vector_table_name} (patient_id)
                        """
                    )
                )
            except Exception:
                pass

        for table_name, columns in expected_columns.items():
            if table_name not in existing_tables:
                continue
            current_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, statement in columns.items():
                if column_name not in current_columns:
                    connection.execute(text(statement))
