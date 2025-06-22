"""
Централизованная обработка исключений для FastAPI приложения.
Маппинг кастомных исключений в HTTP ответы с consistent форматом.
"""

import uuid
from typing import Any, Dict

from core.constants import GeneralErrorMessages, RequestTracing
from core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    DuplicateError,
    ExternalServiceError,
    NotFoundError,
    RepositoryError,
    TokenError,
    ValidationError,
    map_exception_to_http_status,
)
from core.logger import get_logger, set_request_id
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)


class ErrorResponse:
    """Стандартный формат ответа об ошибке"""

    def __init__(
        self,
        error_type: str,
        message: str,
        details: str | None = None,
        request_id: str | None = None,
    ):
        self.error_type = error_type
        self.message = message
        self.details = details
        self.request_id = request_id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для JSON ответа"""
        result = {
            "error": True,
            "error_type": self.error_type,
            "message": self.message,
        }

        if self.details:
            result["details"] = self.details

        if self.request_id:
            result["request_id"] = self.request_id

        return result


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления request_id в каждый запрос"""

    async def dispatch(self, request: Request, call_next):
        # Генерируем или извлекаем request_id
        request_id = request.headers.get(RequestTracing.HEADER_REQUEST_ID) or str(
            uuid.uuid4()
        )

        # Добавляем в state запроса
        request.state.request_id = request_id

        # Устанавливаем request_id в контекст логгера
        set_request_id(request_id)

        try:
            # Выполняем запрос
            response = await call_next(request)

            # Добавляем request_id в заголовки ответа
            response.headers[RequestTracing.HEADER_REQUEST_ID] = request_id

            return response
        finally:
            # Очищаем request_id из контекста после обработки запроса
            from core.logger import clear_request_id

            clear_request_id()


def get_request_id(request: Request) -> str:
    """Получение request_id из запроса"""
    return getattr(request.state, "request_id", "unknown")


# === EXCEPTION HANDLERS ===


async def repository_error_handler(
    request: Request, exc: RepositoryError
) -> JSONResponse:
    """Обработчик ошибок репозитория"""
    request_id = get_request_id(request)

    logger.error(
        f"Repository error: {exc}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "exception_type": type(exc).__name__,
            "exception_details": str(exc),
        },
    )

    status_code = map_exception_to_http_status(exc)
    error_response = ErrorResponse(
        error_type=type(exc).__name__, message=str(exc), request_id=request_id
    )

    return JSONResponse(status_code=status_code, content=error_response.to_dict())


async def authentication_error_handler(
    request: Request, exc: AuthenticationError
) -> JSONResponse:
    """Обработчик ошибок аутентификации"""
    request_id = get_request_id(request)

    logger.warning(
        f"Authentication error: {exc}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "exception_type": type(exc).__name__,
            "user_ip": request.client.host if request.client else "unknown",
        },
    )

    error_response = ErrorResponse(
        error_type="AuthenticationError", message=str(exc), request_id=request_id
    )

    return JSONResponse(status_code=401, content=error_response.to_dict())


async def authorization_error_handler(
    request: Request, exc: AuthorizationError
) -> JSONResponse:
    """Обработчик ошибок авторизации"""
    request_id = get_request_id(request)

    logger.warning(
        f"Authorization error: {exc}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "exception_type": type(exc).__name__,
            "user_ip": request.client.host if request.client else "unknown",
        },
    )

    error_response = ErrorResponse(
        error_type="AuthorizationError", message=str(exc), request_id=request_id
    )

    return JSONResponse(status_code=403, content=error_response.to_dict())


async def token_error_handler(request: Request, exc: TokenError) -> JSONResponse:
    """Обработчик ошибок токенов"""
    request_id = get_request_id(request)

    logger.warning(
        f"Token error: {exc}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "exception_type": type(exc).__name__,
            "token_type": getattr(exc, "token_type", "unknown"),
        },
    )

    error_response = ErrorResponse(
        error_type="TokenError",
        message=str(exc),
        details=f"Token type: {getattr(exc, 'token_type', 'unknown')}",
        request_id=request_id,
    )

    return JSONResponse(status_code=401, content=error_response.to_dict())


async def external_service_error_handler(
    request: Request, exc: ExternalServiceError
) -> JSONResponse:
    """Обработчик ошибок внешніх сервисов"""
    request_id = get_request_id(request)

    logger.error(
        f"External service error: {exc}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "exception_type": type(exc).__name__,
            "service_name": getattr(exc, "service_name", "unknown"),
            "status_code": getattr(exc, "status_code", None),
        },
    )

    error_response = ErrorResponse(
        error_type="ExternalServiceError",
        message=str(exc),
        details=f"Service: {getattr(exc, 'service_name', 'unknown')}",
        request_id=request_id,
    )

    return JSONResponse(status_code=502, content=error_response.to_dict())


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Общий обработчик для неожиданных исключений"""
    request_id = get_request_id(request)

    logger.error(
        f"Unexpected error: {exc}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "exception_type": type(exc).__name__,
            "exception_details": str(exc),
        },
        exc_info=True,
    )

    error_response = ErrorResponse(
        error_type="InternalServerError",
        message=GeneralErrorMessages.INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )

    return JSONResponse(status_code=500, content=error_response.to_dict())


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Обработчик стандартных HTTP исключений FastAPI"""
    request_id = get_request_id(request)

    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            RequestTracing.LOG_REQUEST_ID_KEY: request_id,
            "status_code": exc.status_code,
        },
    )

    error_response = ErrorResponse(
        error_type="HTTPError", message=exc.detail, request_id=request_id
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.to_dict())


# === REGISTRATION HELPER ===


def register_exception_handlers(app):
    """Регистрация всех обработчиков исключений в FastAPI приложении"""

    # Кастомные исключения
    app.add_exception_handler(NotFoundError, repository_error_handler)
    app.add_exception_handler(ValidationError, repository_error_handler)
    app.add_exception_handler(DuplicateError, repository_error_handler)
    app.add_exception_handler(DatabaseError, repository_error_handler)

    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(TokenError, token_error_handler)
    app.add_exception_handler(ExternalServiceError, external_service_error_handler)

    # Стандартные исключения
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Middleware
    app.add_middleware(RequestIDMiddleware)
