from sqlalchemy import text

from cure_quest.config import get_settings
from cure_quest.db.bootstrap import init_database
from cure_quest.db.session import SessionLocal


def main() -> None:
    settings = get_settings()
    init_database()
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    print("DATABASE", settings.database_url)
    print("BRAIN_GATEWAY_MODE", settings.brain_gateway_mode)
    print("STATUS ok")


if __name__ == "__main__":
    main()
