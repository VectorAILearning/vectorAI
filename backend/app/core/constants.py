"""
Константы для сообщений об ошибках.
Централизованное хранение всех текстовых сообщений.
"""

# === AUTH ERROR MESSAGES ===


class AuthErrorMessages:
    """Сообщения об ошибках аутентификации"""

    # Authentication errors
    INVALID_CREDENTIALS = "Неверный email или пароль"
    EMAIL_NOT_VERIFIED = "Email не подтвержден"
    AUTHENTICATION_FAILED = "Ошибка при аутентификации"

    # Registration errors
    USER_ALREADY_EXISTS = "Пользователь уже существует"
    REGISTRATION_FAILED = "Ошибка при регистрации пользователя"

    # Token errors
    INVALID_TOKEN_TYPE = "Неверный тип токена"
    TOKEN_MISSING_EMAIL = "Токен не содержит email"
    TOKEN_EXPIRED = "Токен просрочен"
    INVALID_TOKEN = "Неверный токен"
    REFRESH_TOKEN_NOT_FOUND = "Refresh token не найден"
    REFRESH_TOKEN_REVOKED = "Refresh token отозван"
    REFRESH_TOKEN_EXPIRED = "Refresh token истёк"
    REFRESH_TOKEN_CREATION_FAILED = "Не удалось создать refresh_token"

    # User-related errors
    USER_NOT_FOUND = "Пользователь не найден"
    EMAIL_ALREADY_VERIFIED = "Email уже подтвержден"

    # External service errors
    GOOGLE_TOKEN_FAILED = "Не удалось получить токен от Google"
    GOOGLE_USER_INFO_FAILED = "Не удалось получить информацию о пользователе"
    GOOGLE_EMAIL_MISSING = "Email не получен от Google"

    # Success messages
    EMAIL_VERIFICATION_SENT = (
        "На вашу почту {} отправлено письмо для подтверждения учетной записи"
    )
    PASSWORD_RESET_SENT = "На вашу почту {} отправлено письмо для сброса пароля"
    PASSWORD_UPDATED = "Пароль успешно обновлен!"
    LOGOUT_SUCCESS = "Успешный выход из системы"


# === GENERAL ERROR MESSAGES ===


class GeneralErrorMessages:
    """Общие сообщения об ошибках"""

    INTERNAL_SERVER_ERROR = "Ошибка на стороне сервера"
    SERVICE_UNAVAILABLE = "Сервис временно недоступен"
    VALIDATION_ERROR = "Ошибка валидации данных"
    DATABASE_ERROR = "Ошибка базы данных"


# === REQUEST TRACING ===


class RequestTracing:
    """Константы для трассировки запросов"""

    HEADER_REQUEST_ID = "X-Request-ID"
    LOG_REQUEST_ID_KEY = "request_id"
