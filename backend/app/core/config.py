from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    CHECK_SUBSCRIPTION: bool = True

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_URL: Optional[URL] = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: Optional[str] = None
    REDIS_SESSION_TTL: int = 2592000  # 30 дней по умолчанию

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    DOMAIN: str = "http://127.0.0.1:8000"
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    @field_validator("REDIS_URL", mode="before")
    def assemble_redis_url(cls, v, values):
        if v:
            return v
        host = values.data.get("REDIS_HOST", "localhost")
        port = values.data.get("REDIS_PORT", 6379)
        db = values.data.get("REDIS_DB", 0)
        password = values.data.get("REDIS_PASSWORD", "")
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    @field_validator("POSTGRES_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[URL], values):
        if isinstance(v, URL):
            return v

        return URL.create(
            drivername="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            database=values.data.get("POSTGRES_DB"),
        )

    model_config = SettingsConfigDict(
        env_prefix="AILEARNING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL_AUDIT: str = "gpt-4o-mini"
    OPENAI_MODEL_COURSE_PLAN: str = "gpt-4o-mini"
    OPENAI_MODEL_LESSON_PLAN: str = "gpt-4o-mini"
    OPENAI_MODEL_LESSON_CONTENT: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE_AUDIT: float = 0.2
    OPENAI_TEMPERATURE_COURSE_PLAN: float = 0.3
    OPENAI_TEMPERATURE_LESSON_PLAN: float = 0.3
    OPENAI_TEMPERATURE_LESSON_CONTENT: float = 0.3
    AUDIT_MAX_QUESTIONS: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class GenerationSettings(BaseSettings):
    GENERATION_MAX_MODULES: int = 2
    GENERATION_MAX_LESSONS: int = 2
    GENERATION_MAX_CONTENTS: int = 10


settings = Settings()
openai_settings = OpenAISettings()
generation_settings = GenerationSettings()
