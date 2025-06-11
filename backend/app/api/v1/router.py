from fastapi import APIRouter

from .audit import audit_router
from .auth import auth_router
from .code import code_router
from .courses import courses_router
from .generate import generate_router
from .tasks import tasks_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(audit_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(generate_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(tasks_router)
api_v1_router.include_router(code_router)
