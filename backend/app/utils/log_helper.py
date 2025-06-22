"""
Вспомогательные функции для централизованного логирования.
Предоставляет удобные API для различных типов логирования.
"""

import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from core.logger import VectorAILogger, get_logger
from fastapi import Request


def log_api_request(
    request: Request,
    logger: VectorAILogger,
    method: str,
    path: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    user_id: Optional[str] = None,
    **additional_context,
):
    """
    Логирование API запроса с контекстной информацией.

    Args:
        request: FastAPI Request объект
        logger: Экземпляр логгера
        method: HTTP метод
        path: Путь запроса
        status_code: Код ответа (если доступен)
        duration_ms: Время выполнения в миллисекундах
        user_id: ID пользователя (если авторизован)
        **additional_context: Дополнительный контекст
    """

    # Базовый контекст API запроса
    context = {
        "event_type": "api_request",
        "method": method,
        "path": path,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        **additional_context,
    }

    # Добавляем опциональные поля
    if status_code:
        context["status_code"] = status_code

    if duration_ms:
        context["duration_ms"] = round(duration_ms, 2)

    if user_id:
        context["user_id"] = user_id

    # Выбираем уровень логирования по статус коду
    if status_code:
        if status_code >= 500:
            logger.error(f"API {method} {path} - {status_code}", **context)
        elif status_code >= 400:
            logger.warning(f"API {method} {path} - {status_code}", **context)
        else:
            logger.info(f"API {method} {path} - {status_code}", **context)
    else:
        logger.info(f"API {method} {path}", **context)


def log_business_event(
    logger: VectorAILogger,
    event_name: str,
    user_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    **additional_context,
):
    """
    Логирование бизнес-события (регистрация, вход, смена пароля и т.д.).

    Args:
        logger: Экземпляр логгера
        event_name: Название события
        user_id: ID пользователя
        entity_type: Тип сущности (user, post, etc.)
        entity_id: ID сущности
        **additional_context: Дополнительный контекст
    """

    context = {
        "event_type": "business_event",
        "event_name": event_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **additional_context,
    }

    if user_id:
        context["user_id"] = user_id

    if entity_type:
        context["entity_type"] = entity_type

    if entity_id:
        context["entity_id"] = entity_id

    logger.info(f"Business Event: {event_name}", **context)


def log_error_with_context(
    logger: VectorAILogger,
    error: Exception,
    operation: str,
    user_id: Optional[str] = None,
    **additional_context,
):
    """
    Логирование ошибки с расширенным контекстом.

    Args:
        logger: Экземпляр логгера
        error: Исключение
        operation: Описание операции во время которой произошла ошибка
        user_id: ID пользователя (если доступен)
        **additional_context: Дополнительный контекст
    """

    context = {
        "event_type": "error",
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        **additional_context,
    }

    if user_id:
        context["user_id"] = user_id

    logger.exception(f"Error during {operation}: {error}", **context)


def log_auth_event(
    logger: VectorAILogger,
    event_type: str,
    user_email: str,
    success: bool,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    **additional_context,
):
    """
    Логирование событий аутентификации.

    Args:
        logger: Экземпляр логгера
        event_type: Тип события (login, logout, register, etc.)
        user_email: Email пользователя
        success: Успешность операции
        client_ip: IP адрес клиента
        user_agent: User Agent браузера
        **additional_context: Дополнительный контекст
    """

    context = {
        "event_type": "auth_event",
        "auth_event_type": event_type,
        "user_email": user_email,
        "success": success,
        **additional_context,
    }

    if client_ip:
        context["client_ip"] = client_ip

    if user_agent:
        context["user_agent"] = user_agent

    message = f"Auth {event_type}: {user_email} - {'SUCCESS' if success else 'FAILED'}"

    if success:
        logger.info(message, **context)
    else:
        logger.warning(message, **context)


def log_performance(
    logger: VectorAILogger, operation: str, duration_ms: float, **additional_context
):
    """
    Логирование производительности операций.

    Args:
        logger: Экземпляр логгера
        operation: Название операции
        duration_ms: Время выполнения в миллисекундах
        **additional_context: Дополнительный контекст
    """

    context = {
        "event_type": "performance",
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        **additional_context,
    }

    # Логируем как warning если операция медленная
    if duration_ms > 1000:  # > 1 секунды
        logger.warning(
            f"Slow operation: {operation} took {duration_ms:.2f}ms", **context
        )
    elif duration_ms > 500:  # > 500ms
        logger.info(f"Operation: {operation} took {duration_ms:.2f}ms", **context)
    else:
        logger.debug(f"Operation: {operation} took {duration_ms:.2f}ms", **context)


@contextmanager
def log_operation_duration(
    logger: VectorAILogger, operation: str, **additional_context
):
    """
    Контекстный менеджер для автоматического логирования времени выполнения операции.

    Usage:
        with log_operation_duration(logger, "user_registration"):
            # код регистрации пользователя
            pass
    """

    start_time = time.time()

    try:
        logger.debug(
            f"Starting operation: {operation}",
            event_type="operation_start",
            operation=operation,
            **additional_context,
        )
        yield

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error_with_context(
            logger, e, operation, duration_ms=duration_ms, **additional_context
        )
        raise

    else:
        duration_ms = (time.time() - start_time) * 1000
        log_performance(logger, operation, duration_ms, **additional_context)


def sanitize_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очистка чувствительных данных для безопасного логирования.

    Args:
        data: Словарь с данными

    Returns:
        Очищенный словарь
    """

    sensitive_keys = {
        "password",
        "passwd",
        "secret",
        "token",
        "key",
        "auth",
        "credential",
        "authorization",
        "api_key",
        "private_key",
    }

    cleaned_data = {}

    for key, value in data.items():
        key_lower = key.lower()

        # Проверяем наличие чувствительных ключей
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            cleaned_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            # Рекурсивно очищаем вложенные словари
            cleaned_data[key] = sanitize_sensitive_data(value)
        else:
            cleaned_data[key] = value

    return cleaned_data


# Удобные функции для создания специализированных логгеров
def create_api_logger() -> VectorAILogger:
    """Создание логгера для API endpoints"""
    return get_logger("vectorai.api")


def create_auth_logger() -> VectorAILogger:
    """Создание логгера для аутентификации"""
    return get_logger("vectorai.auth")


def create_business_logger() -> VectorAILogger:
    """Создание логгера для бизнес-логики"""
    return get_logger("vectorai.business")


def create_db_logger() -> VectorAILogger:
    """Создание логгера для базы данных"""
    return get_logger("vectorai.database")


def create_email_logger() -> VectorAILogger:
    """Создание логгера для email отправки"""
    return get_logger("vectorai.email")
