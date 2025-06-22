"""
Централизованная система логирования для VectorAI.
Поддерживает structured logging с request_id трассировкой.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.constants import RequestTracing


class LogLevel(str, Enum):
    """Уровни логирования"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Форматы логирования"""

    JSON = "JSON"
    TEXT = "TEXT"


# Context variable для хранения request_id
request_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Форматтер для structured logging в JSON формате"""

    def format(self, record: logging.LogRecord) -> str:
        """Форматирование лог записи в JSON"""

        # Базовая структура лога
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Добавляем request_id если доступен
        request_id = request_context.get()
        if request_id:
            log_data[RequestTracing.LOG_REQUEST_ID_KEY] = request_id

        # Добавляем дополнительные поля из extra
        if hasattr(record, "extra") and getattr(record, "extra", None):
            extra_data = getattr(record, "extra")
            if isinstance(extra_data, dict):
                log_data.update(extra_data)

        # Добавляем информацию об исключении если есть
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Добавляем стэк трейс для ERROR+ уровней
        if record.levelno >= logging.ERROR and record.stack_info:
            log_data["stack_trace"] = self.formatStack(record.stack_info)

        return json.dumps(log_data, ensure_ascii=False, separators=(",", ":"))


class ReadableFormatter(logging.Formatter):
    """Человекочитаемый форматтер для development"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        """Форматирование в читаемом виде с request_id"""

        # Базовое форматирование
        formatted = super().format(record)

        # Добавляем request_id если доступен
        request_id = request_context.get()
        if request_id:
            formatted = f"[{request_id[:8]}] {formatted}"

        return formatted


class VectorAILogger:
    """Централизованный логгер для VectorAI"""

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        format_type: LogFormat = LogFormat.TEXT,
        file_path: Optional[str] = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # Очищаем существующие handlers
        self.logger.handlers.clear()

        # Настраиваем форматтер
        if format_type == LogFormat.JSON:
            formatter = StructuredFormatter()
        else:
            formatter = ReadableFormatter()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (опционально)
        if file_path:
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Предотвращаем дублирование логов
        self.logger.propagate = False

    def _log_with_context(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """Внутренний метод логирования с контекстом"""

        # Подготавливаем extra данные
        log_extra = extra or {}

        # Логируем с дополнительной информацией
        self.logger.log(
            level,
            message,
            extra={"extra": log_extra},
            exc_info=exc_info,
            stack_info=level >= logging.ERROR,
        )

    def debug(self, message: str, **context):
        """Debug уровень логирования"""
        self._log_with_context(logging.DEBUG, message, context)

    def info(self, message: str, **context):
        """Info уровень логирования"""
        self._log_with_context(logging.INFO, message, context)

    def warning(self, message: str, **context):
        """Warning уровень логирования"""
        self._log_with_context(logging.WARNING, message, context)

    def error(self, message: str, **context):
        """Error уровень логирования"""
        self._log_with_context(logging.ERROR, message, context, exc_info=True)

    def critical(self, message: str, **context):
        """Critical уровень логирования"""
        self._log_with_context(logging.CRITICAL, message, context, exc_info=True)

    def exception(self, message: str, **context):
        """Логирование исключения с полным стэк трейсом"""
        self._log_with_context(logging.ERROR, message, context, exc_info=True)


def set_request_id(request_id: str):
    """Установка request_id в контекст"""
    request_context.set(request_id)


def get_request_id() -> Optional[str]:
    """Получение текущего request_id"""
    return request_context.get()


def clear_request_id():
    """Очистка request_id из контекста"""
    request_context.set(None)


# Глобальная фабрика логгеров
_loggers: Dict[str, VectorAILogger] = {}


def get_logger(
    name: str,
    level: Optional[LogLevel] = None,
    format_type: Optional[LogFormat] = None,
    file_path: Optional[str] = None,
) -> VectorAILogger:
    """
    Фабричная функция для получения логгера.

    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования
        format_type: Формат логов (JSON/TEXT)
        file_path: Путь к файлу логов (опционально)

    Returns:
        Экземпляр VectorAILogger
    """

    # Создаем ключ для кэширования
    cache_key = f"{name}_{level}_{format_type}_{file_path}"

    if cache_key not in _loggers:
        # Устанавливаем значения по умолчанию из настроек
        from core.config import settings

        # Используем настройки из config если не переданы явно
        actual_level = level or LogLevel(settings.LOG_LEVEL)
        actual_format = format_type or LogFormat(settings.LOG_FORMAT)
        actual_file_path = file_path or settings.LOG_FILE

        _loggers[cache_key] = VectorAILogger(
            name=name,
            level=actual_level,
            format_type=actual_format,
            file_path=actual_file_path,
        )

    return _loggers[cache_key]


# Удобная функция для быстрого получения логгера
def create_logger(name: str) -> VectorAILogger:
    """Создание логгера с настройками по умолчанию"""
    return get_logger(name)
