"""Асинхронное подключение к PostgreSQL через SQLAlchemy 2.0."""

from collections.abc import AsyncGenerator
from typing import Self

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings


class DatabaseManager:
    """
    Singleton-менеджер подключения к PostgreSQL.

    Инкапсулирует async engine и фабрику сессий.
    Инициализируется один раз при старте приложения.
    """

    _instance: "DatabaseManager | None" = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._initialized = True

    @property
    def engine(self) -> AsyncEngine:
        """Возвращает async engine. Вызывает ошибку, если не инициализирован."""
        if self._engine is None:
            msg = "DatabaseManager не инициализирован. Вызовите init() при старте приложения."
            raise RuntimeError(msg)
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Возвращает фабрику async-сессий."""
        if self._session_factory is None:
            msg = "DatabaseManager не инициализирован. Вызовите init() при старте приложения."
            raise RuntimeError(msg)
        return self._session_factory

    @property
    def is_initialized(self) -> bool:
        """Проверяет, инициализирован ли менеджер."""
        return self._engine is not None and self._session_factory is not None

    def init(self, settings: Settings | None = None) -> None:
        """
        Создаёт async engine и session factory.

        Args:
            settings: Настройки приложения. Если не переданы — загружаются через get_settings().
        """
        if self.is_initialized:
            return

        cfg = settings or get_settings()

        self._engine = create_async_engine(
            url=cfg.sqlalchemy_database_uri,
            echo=cfg.app_debug and cfg.is_development,
            pool_size=cfg.db_pool_size,
            max_overflow=cfg.db_max_overflow,
            pool_timeout=cfg.db_pool_timeout,
            pool_recycle=cfg.db_pool_recycle,
            pool_pre_ping=True,  # Проверка «живости» соединения перед использованием
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def close(self) -> None:
        """Корректно закрывает пул соединений."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def health_check(self) -> bool:
        """
        Проверяет доступность PostgreSQL.

        Returns:
            True, если БД отвечает на запрос SELECT 1.
        """
        if not self.is_initialized:
            return False

        try:
            async with self.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar_one() == 1
        except Exception:
            return False

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Асинхронный генератор сессии для Dependency Injection.

        Yields:
            AsyncSession: Сессия SQLAlchemy с автоматическим rollback при ошибке.
        """
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


# Глобальный singleton-экземпляр менеджера БД
db_manager = DatabaseManager()


def init_db(settings: Settings | None = None) -> None:
    """Инициализирует подключение к PostgreSQL."""
    db_manager.init(settings)


async def close_db() -> None:
    """Закрывает подключение к PostgreSQL."""
    await db_manager.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency для получения async-сессии БД.

    Yields:
        AsyncSession: Активная сессия SQLAlchemy.
    """
    async for session in db_manager.get_session():
        yield session
