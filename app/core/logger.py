"""Конфигурация логирования через logging.config."""

import logging
import logging.config
import sys
from typing import Any

from app.core.config import Settings, get_settings

# Имя корневого логгера приложения
LOGGER_NAME = "ai_assistant"


class RequestIdFilter(logging.Filter):
    """
    Фильтр для добавления request_id в записи лога.

    Значение request_id устанавливается middleware через ContextVar.
    Если контекст недоступен — используется «-».
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Ленивый импорт, чтобы избежать циклических зависимостей
        try:
            from app.middleware.request_context import get_request_id

            record.request_id = get_request_id() or "-"
        except ImportError:
            record.request_id = "-"

        return True


def _build_logging_config(settings: Settings) -> dict[str, Any]:
    """
    Строит dictConfig для logging.

    В production используется JSON-подобный формат,
    в development — читаемый текстовый вывод.
    """
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "request_id=%(request_id)s | %(message)s"
    )

    if settings.is_production:
        # Компактный формат для агрегаторов логов (ELK, Loki, CloudWatch)
        log_format = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","request_id":"%(request_id)s",'
            '"message":"%(message)s"}'
        )

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {
                "()": RequestIdFilter,
            },
        },
        "formatters": {
            "default": {
                "format": log_format,
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "filters": ["request_id"],
                "stream": sys.stdout,
            },
        },
        "loggers": {
            LOGGER_NAME: {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Подавляем избыточный шум от uvicorn access-логов в production
            "uvicorn.access": {
                "level": "WARNING" if settings.is_production else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"],
        },
    }


def setup_logging(settings: Settings | None = None) -> None:
    """
    Инициализирует систему логирования.

    Вызывается один раз при старте приложения в lifespan.

    Args:
        settings: Настройки приложения. Если не переданы — загружаются через get_settings().
    """
    cfg = settings or get_settings()
    logging.config.dictConfig(_build_logging_config(cfg))


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Возвращает именованный логгер приложения.

    Args:
        name: Суффикс имени логгера (например, «auth», «db»).
              Итоговое имя: ai_assistant.auth

    Returns:
        logging.Logger: Настроенный логгер.
    """
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)
