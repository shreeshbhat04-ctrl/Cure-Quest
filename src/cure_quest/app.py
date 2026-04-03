from contextlib import asynccontextmanager

from fastapi import FastAPI

from cure_quest.api.routes import router
from cure_quest.config import get_settings
from cure_quest.db.bootstrap import init_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
