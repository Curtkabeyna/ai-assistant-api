"""FastAPI Dependency Injection провайдеры."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.database import get_db as _get_db
from app.db.redis import get_redis as _get_redis

# --- Settings ---

SettingsDep = Annotated[Settings, Depends(get_settings)]


# --- Database ---

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency: async-сессия PostgreSQL.

    Yields:
        AsyncSession: Сессия SQLAlchemy 2.0 с автоматическим rollback при ошибке.
    """
    async for session in _get_db():
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


# --- Redis ---

def get_redis() -> Redis:
    """
    Dependency: async Redis-клиент.

    Returns:
        Redis: Клиент из singleton RedisManager.
    """
    return _get_redis()


RedisDep = Annotated[Redis, Depends(get_redis)]
