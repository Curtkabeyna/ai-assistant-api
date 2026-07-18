"""Кастомные исключения и обработчики ошибок FastAPI."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger import get_logger

logger = get_logger("exceptions")


class ErrorResponse(BaseModel):
    """Стандартизированный формат ответа об ошибке."""

    detail: str = Field(description="Описание ошибки")
    error_code: str = Field(description="Машиночитаемый код ошибки")
    status_code: int = Field(description="HTTP-статус")


class AppException(Exception):
    """
    Базовое исключение приложения.

    Все доменные ошибки наследуются от этого класса
    и автоматически маппятся в HTTP-ответ через exception handler.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "Внутренняя ошибка сервера"

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        if error_code is not None:
            self.error_code = error_code
        self.details = details
        super().__init__(self.message)

    def to_response(self) -> ErrorResponse:
        """Преобразует исключение в Pydantic-модель ответа."""
        return ErrorResponse(
            detail=self.message,
            error_code=self.error_code,
            status_code=self.status_code,
        )


class NotFoundError(AppException):
    """Ресурс не найден (404)."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    message = "Ресурс не найден"


class UnauthorizedError(AppException):
    """Не авторизован (401)."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "UNAUTHORIZED"
    message = "Требуется аутентификация"


class ForbiddenError(AppException):
    """Доступ запрещён (403)."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"
    message = "Недостаточно прав для выполнения операции"


class ConflictError(AppException):
    """Конфликт данных (409)."""

    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"
    message = "Конфликт данных"


class BadRequestError(AppException):
    """Некорректный запрос (400)."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "BAD_REQUEST"
    message = "Некорректный запрос"


class ValidationAppError(AppException):
    """Ошибка валидации бизнес-логики (422)."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    message = "Ошибка валидации данных"


class ServiceUnavailableError(AppException):
    """Сервис временно недоступен (503)."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"
    message = "Сервис временно недоступен"


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Обработчик доменных исключений AppException."""
    logger.warning(
        "AppException: code=%s status=%d message=%s",
        exc.error_code,
        exc.status_code,
        exc.message,
    )
    error = exc.to_response()
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
    )


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Обработчик стандартных HTTP-исключений Starlette/FastAPI."""
    error = ErrorResponse(
        detail=str(exc.detail),
        error_code="HTTP_ERROR",
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
    )


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обработчик ошибок валидации Pydantic/FastAPI."""
    errors = exc.errors()
    detail = "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in errors
    )
    logger.debug("Validation error: %s", detail)

    error = ErrorResponse(
        detail=detail,
        error_code="VALIDATION_ERROR",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            **error.model_dump(),
            "errors": errors,  # Детали для клиента API
        },
    )


async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Обработчик неперехваченных исключений (500)."""
    logger.exception("Unhandled exception: %s", exc)

    error = ErrorResponse(
        detail="Внутренняя ошибка сервера",
        error_code="INTERNAL_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Регистрирует все exception handlers в FastAPI-приложении.

    Args:
        app: Экземпляр FastAPI.
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
