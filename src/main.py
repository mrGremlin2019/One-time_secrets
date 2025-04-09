"""
Точка входа в приложение FastAPI
"""

from fastapi import FastAPI
import asyncio
from src.api.routers import router
from src.middleware import NoCacheHeadersMiddleware
from src.db.config_db import engine
from src.db.models import Base
from src.tasks.ttl_checker import TTLChecker
import logging

app = FastAPI(
    title="One-time Secrets API",
    description="Сервис для одноразового хранения и получения зашифрованных секретов.",
    version="1.0.0"
)

logger = logging.getLogger(__name__)
ttl_checker = TTLChecker()

def init_db():
    """Инициализация таблиц БД"""
    Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    init_db()
    asyncio.create_task(ttl_checker.check_expired_secrets())
    logger.info("Application started")

# Подключаем API роутеры
app.include_router(router)

# Подключаем middleware для запрета кеширования
app.add_middleware(NoCacheHeadersMiddleware)
