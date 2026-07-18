"""Обратная совместимость: re-export из database.py."""

from app.db.database import close_db, db_manager, get_db, init_db

__all__ = ["close_db", "db_manager", "get_db", "init_db"]
