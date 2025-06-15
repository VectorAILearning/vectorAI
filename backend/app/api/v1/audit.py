import logging

from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from schemas.session import SessionInfoResponse
from services import RedisCacheService, get_cache_service
from services.session_service.service import SessionService
from utils.uow import UnitOfWork, get_uow

audit_router = APIRouter(prefix="/audit", tags=["audit"])
log = logging.getLogger(__name__)


@audit_router.post("/reset-chat", response_model=SessionInfoResponse)
async def reset_chat(
    request: Request,
    redis_service: RedisCacheService = Depends(get_cache_service),
    uow: UnitOfWork = Depends(get_uow),
):
    sid = request.cookies.get(settings.SESSION_COOKIE_KEY)
    if not sid:
        raise HTTPException(status_code=400, detail="Session not found")

    await redis_service.reset_chat(sid)
    await redis_service.set_session_status(sid, "chating")
    info = await redis_service.get_session_info(sid)
    if not info:
        raise HTTPException(status_code=400, detail="Failed to get session info")
    return SessionInfoResponse(**info)


@audit_router.get("/session-info", response_model=SessionInfoResponse)
async def get_session_info(
    request: Request,
    response: Response,
    redis_service: RedisCacheService = Depends(get_cache_service),
    uow: UnitOfWork = Depends(get_uow),
):
    sid = request.cookies.get(settings.SESSION_COOKIE_KEY)
    if not sid:
        info = await SessionService(uow).create_session()
        response.set_cookie(
            key=settings.SESSION_COOKIE_KEY,
            value=info["session_id"],
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=settings.SESSION_TTL,
        )
        return SessionInfoResponse(**info)

    info = await redis_service.get_session_info(sid)
    if not info:
        info = await SessionService(uow).create_session()
        response.set_cookie(
            key=settings.SESSION_COOKIE_KEY,
            value=info["session_id"],
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=settings.SESSION_TTL,
        )

    return SessionInfoResponse(**info)
