import logging
import sys

from api.v1.router import api_v1_router
from core.config import settings
from core.exception_handler import register_exception_handlers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

log = logging.getLogger(__name__)

app = FastAPI(
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

ALLOW_ORIGINS = [settings.DOMAIN]

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
