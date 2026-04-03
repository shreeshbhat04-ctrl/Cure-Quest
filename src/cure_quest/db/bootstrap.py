from cure_quest.db.session import Base, engine


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
