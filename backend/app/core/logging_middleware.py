"""
Middleware для автоматического логирования API запросов.
"""

import time
from typing import Callable

from core.logger import get_logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.log_helper import log_api_request


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования всех API запросов и ответов"""

    def __init__(self, app, logger_name: str = "vectorai.api"):
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Обработка запроса с логированием"""

        start_time = time.time()

        # Извлекаем базовую информацию о запросе
        method = request.method
        path = str(request.url.path)

        # Логируем начало запроса
        self.logger.info(
            f"API Request started: {method} {path}",
            event_type="api_request_start",
            method=method,
            path=path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        try:
            # Выполняем запрос
            response = await call_next(request)

            # Вычисляем время выполнения
            duration_ms = (time.time() - start_time) * 1000

            # Логируем завершение запроса
            log_api_request(
                request=request,
                logger=self.logger,
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            return response

        except Exception as e:
            # Логируем ошибку
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                f"API Request failed: {method} {path}",
                event_type="api_request_error",
                method=method,
                path=path,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=duration_ms,
                client_ip=request.client.host if request.client else None,
            )

            # Повторно поднимаем исключение
            raise
