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
        "prescriptions": {
            "document_drive_file_id": "ALTER TABLE prescriptions ADD COLUMN document_drive_file_id VARCHAR(255)",
            "document_drive_file_url": "ALTER TABLE prescriptions ADD COLUMN document_drive_file_url TEXT",
        },
        "escalation_cases": {
            "external_ticket_url": "ALTER TABLE escalation_cases ADD COLUMN external_ticket_url TEXT",
            "drive_file_id": "ALTER TABLE escalation_cases ADD COLUMN drive_file_id VARCHAR(255)",
            "drive_file_url": "ALTER TABLE escalation_cases ADD COLUMN drive_file_url TEXT",
            "calendar_event_id": "ALTER TABLE escalation_cases ADD COLUMN calendar_event_id VARCHAR(255)",
            "calendar_event_url": "ALTER TABLE escalation_cases ADD COLUMN calendar_event_url TEXT",
            "pharmacy_search_summary": "ALTER TABLE escalation_cases ADD COLUMN pharmacy_search_summary TEXT",
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
