"""Управление жизненным циклом FastAPI-приложения."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logger import get_logger, setup_logging
from app.db.database import close_db, db_manager, init_db
from app.db.redis import close_redis, init_redis, redis_manager

logger = get_logger("lifespan")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Async context manager жизненного цикла приложения.

    Startup:
        1. Настройка логирования
        2. Инициализация PostgreSQL (async engine + session factory)
        3. Инициализация Redis (connection pool)
        4. Проверка health check зависимостей

    Shutdown:
        1. Закрытие Redis
        2. Закрытие PostgreSQL

    Args:
        _app: Экземпляр FastAPI (зарезервирован для будущих расширений).

    Yields:
        None: Управление передаётся FastAPI на время работы приложения.
    """
    settings = get_settings()

    # --- Startup ---
    setup_logging(settings)
    logger.info(
        "Запуск приложения: env=%s debug=%s",
        settings.app_env,
        settings.app_debug,
    )

    init_db(settings)
    init_redis(settings)
    logger.info("Инфраструктура инициализирована")

    # Проверяем доступность зависимостей при старте
    db_ok = await db_manager.health_check()
    redis_ok = await redis_manager.health_check()

    if not db_ok:
        logger.error("PostgreSQL недоступен при старте приложения")
    if not redis_ok:
        logger.error("Redis недоступен при старте приложения")

    if db_ok and redis_ok:
        logger.info("Health check пройден: PostgreSQL и Redis доступны")
    else:
        logger.warning(
            "Приложение запущено с недоступными зависимостями: db=%s redis=%s",
            db_ok,
            redis_ok,
        )

    yield

    # --- Shutdown ---
    logger.info("Остановка приложения...")
    await close_redis()
    await close_db()
    logger.info("Приложение остановлено")
