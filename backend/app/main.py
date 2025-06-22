from api.v1.router import api_v1_router
from core.config import settings
from core.exception_handler import register_exception_handlers
from core.logger import get_logger
from core.logging_middleware import APILoggingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Создаем централизованный логгер для приложения
log = get_logger(__name__)

app = FastAPI(
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

ALLOW_ORIGINS = [settings.DOMAIN]

# API логирование middleware (добавляем перед CORS)
app.add_middleware(APILoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация обработчиков исключений
register_exception_handlers(app)

app.include_router(api_v1_router)

# Логирование старта приложения
log.info(
    "VectorAI Backend application started",
    app_name="VectorAI",
    version="1.0.0",
    domain=settings.DOMAIN,
)
