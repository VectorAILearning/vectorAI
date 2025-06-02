from fastapi import APIRouter

from .audit import audit_router
from .auth import auth_router
from .courses import courses_router
from .lessons import lessons_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(audit_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(lessons_router)
api_v1_router.include_router(auth_router)
