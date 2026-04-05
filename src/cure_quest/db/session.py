from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from cure_quest.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
resolved_database_url = settings.resolved_database_url
connect_args = {"check_same_thread": False} if resolved_database_url.startswith("sqlite") else {}
engine = create_engine(resolved_database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
