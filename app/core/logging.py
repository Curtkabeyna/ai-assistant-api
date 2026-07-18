"""Обратная совместимость: re-export из logger.py."""

from app.core.logger import get_logger, setup_logging

__all__ = ["get_logger", "setup_logging"]
