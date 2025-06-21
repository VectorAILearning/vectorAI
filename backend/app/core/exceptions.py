"""
Кастомные исключения для чистой архитектуры.
Репозитории используют эти исключения вместо HTTP-специфичных ошибок.
"""

from typing import Any

from fastapi import status


class RepositoryError(Exception):
    """Базовое исключение для всех ошибок репозитория"""

    pass


class NotFoundError(RepositoryError):
    """Исключение когда объект не найден в БД"""

    def __init__(self, model_name: str, identifier: Any):
        self.model_name = model_name
        self.identifier = identifier
        super().__init__(f"{model_name} с ID '{identifier}' не найден")


class ValidationError(RepositoryError):
    """Исключение валидации данных на уровне репозитория"""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


class DuplicateError(RepositoryError):
    """Исключение когда создается дубликат уникального объекта"""

    def __init__(self, model_name: str, field: str, value: Any):
        self.model_name = model_name
        self.field = field
        self.value = value
        super().__init__(f"{model_name} с {field}='{value}' уже существует")


class DatabaseError(RepositoryError):
    """Исключение для ошибок базы данных на уровне репозитория"""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)


# === AUTH SERVICE EXCEPTIONS ===


class AuthenticationError(Exception):
    """Исключение для ошибок аутентификации пользователя"""

    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message)


class AuthorizationError(Exception):
    """Исключение для ошибок авторизации (доступ запрещен)"""

    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(message)


class TokenError(Exception):
    """Исключение для ошибок работы с токенами (JWT, refresh tokens)"""

    def __init__(self, message: str, token_type: str | None = None):
        self.token_type = token_type
        super().__init__(message)


class ExternalServiceError(Exception):
    """Исключение для ошибок внешних сервисов (Google, API)"""

    def __init__(self, service_name: str, message: str, status_code: int | None = None):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(f"Ошибка {service_name}: {message}")


# === EXCEPTION TO HTTP STATUS MAPPER ===


def map_exception_to_http_status(exception: Exception) -> int:
    """
    Маппинг кастомных исключений в HTTP статус коды.

    Args:
        exception: Исключение для маппинга

    Returns:
        HTTP status code
    """
    if isinstance(exception, NotFoundError):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(exception, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exception, DuplicateError):
        return status.HTTP_409_CONFLICT
    elif isinstance(exception, DatabaseError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exception, AuthenticationError):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exception, AuthorizationError):
        return status.HTTP_403_FORBIDDEN
    elif isinstance(exception, TokenError):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exception, ExternalServiceError):
        return status.HTTP_502_BAD_GATEWAY
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
