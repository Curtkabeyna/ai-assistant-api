"""Асинхронное подключение к Redis."""

from typing import Any, Self

from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError

from app.core.config import Settings, get_settings


class RedisManager:
    """
    Singleton-менеджер подключения к Redis.

    Управляет пулом соединений и предоставляет клиент для DI.
    """

    _instance: "RedisManager | None" = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None
        self._initialized = True

    @property
    def client(self) -> Redis:
        """Возвращает async Redis-клиент."""
        if self._client is None:
            msg = "RedisManager не инициализирован. Вызовите init() при старте приложения."
            raise RuntimeError(msg)
        return self._client

    @property
    def is_initialized(self) -> bool:
        """Проверяет, инициализирован ли менеджер."""
        return self._client is not None and self._pool is not None

    def init(self, settings: Settings | None = None) -> None:
        """
        Создаёт пул соединений и Redis-клиент.

        Args:
            settings: Настройки приложения. Если не переданы — загружаются через get_settings().
        """
        if self.is_initialized:
            return

        cfg = settings or get_settings()

        self._pool = ConnectionPool.from_url(
            url=cfg.redis_dsn,
            max_connections=cfg.redis_max_connections,
            socket_timeout=cfg.redis_socket_timeout,
            socket_connect_timeout=cfg.redis_socket_connect_timeout,
            decode_responses=True,  # Автоматическое декодирование bytes → str
        )

        self._client = Redis(connection_pool=self._pool)

    async def close(self) -> None:
        """Корректно закрывает клиент и пул соединений."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

        if self._pool is not None:
            await self._pool.aclose()
            self._pool = None

    async def health_check(self) -> bool:
        """
        Проверяет доступность Redis.

        Returns:
            True, если Redis отвечает на PING.
        """
        if not self.is_initialized:
            return False

        try:
            return await self._client.ping()  # type: ignore[union-attr]
        except RedisError:
            return False

    async def get(self, key: str) -> str | None:
        """Получает значение по ключу."""
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str | bytes | int | float,
        *,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
    ) -> bool | None:
        """Устанавливает значение по ключу с опциональным TTL."""
        return await self.client.set(key, value, ex=ex, px=px, nx=nx)

    async def delete(self, *keys: str) -> int:
        """Удаляет один или несколько ключей."""
        return await self.client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """Проверяет существование ключей."""
        return await self.client.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        """Устанавливает TTL для ключа."""
        return await self.client.expire(key, seconds)

    async def get_json(self, key: str) -> Any | None:
        """
        Получает и десериализует JSON-значение.

        Note:
            Использует встроенный метод Redis JSON, если доступен,
            иначе — ручной парсинг через стандартный json.
        """
        import json

        raw = await self.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set_json(self, key: str, value: Any, *, ex: int | None = None) -> bool | None:
        """Сериализует и сохраняет JSON-значение."""
        import json

        return await self.set(key, json.dumps(value, ensure_ascii=False), ex=ex)


# Глобальный singleton-экземпляр менеджера Redis
redis_manager = RedisManager()


def init_redis(settings: Settings | None = None) -> None:
    """Инициализирует подключение к Redis."""
    redis_manager.init(settings)


async def close_redis() -> None:
    """Закрывает подключение к Redis."""
    await redis_manager.close()


def get_redis() -> Redis:
    """
    FastAPI dependency для получения Redis-клиента.

    Returns:
        Redis: Асинхронный клиент Redis.
    """
    return redis_manager.client
