import logging

from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from schemas.session import SessionInfoResponse
from services import RedisCacheService, get_cache_service
from services.session_service.service import SessionService
from utils.auth_utils import decode_access_token
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
    user_id = None
    access_token = request.headers.get("Authorization")

    if access_token:
        token_payload = decode_access_token(access_token.split(" ")[1])
        if token_payload:
            email = token_payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")
            user = await uow.auth_repo.get_by_email(email)
            if user:
                user_id = str(user.id)
            else:
                raise HTTPException(status_code=401, detail="User not found")
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

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
        if user_id:
            await SessionService(uow).attach_user(info["session_id"], user_id)
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
        if user_id:
            await SessionService(uow).attach_user(info["session_id"], user_id)

    return SessionInfoResponse(**info)
