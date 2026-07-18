"""ContextVar для хранения request-scoped данных."""

from contextvars import ContextVar

# Уникальный идентификатор запроса (устанавливается middleware)
_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Возвращает request_id текущего запроса."""
    return _request_id_var.get()


def set_request_id(request_id: str) -> None:
    """Устанавливает request_id для текущего контекста."""
    _request_id_var.set(request_id)
