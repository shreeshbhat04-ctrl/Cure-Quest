from pprint import pprint

from sqlalchemy import text

from cure_quest.config import get_settings
from cure_quest.db.session import engine


def main() -> None:
    settings = get_settings()
    result = {
        "database_url_hint": settings.database_backend_hint,
        "vector_table": settings.medical_vector_table_name,
    }
    with engine.begin() as connection:
        if engine.dialect.name != "postgresql":
            result["ready"] = False
            result["reason"] = "Vector setup requires a Postgres/AlloyDB database."
            pprint(result)
            return

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
                f"CREATE INDEX IF NOT EXISTS idx_{settings.medical_vector_table_name}_patient_id "
                f"ON {settings.medical_vector_table_name} (patient_id)"
            )
        )

    result["ready"] = True
    pprint(result)


if __name__ == "__main__":
    main()
