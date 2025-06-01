from fastapi import APIRouter, Depends, Request
from schemas.session import SessionInfoResponse
from services import RedisCacheService, get_cache_service
from services.session_service.service import SessionService
from utils.uow import UnitOfWork, get_uow

audit_router = APIRouter(prefix="/audit", tags=["audit"])


@audit_router.post("/reset-chat", response_model=SessionInfoResponse)
async def reset_chat(
    request: Request,
    redis_service: RedisCacheService = Depends(get_cache_service),
    uow: UnitOfWork = Depends(get_uow),
):
    ip = request.client.host
    device = request.headers.get("user-agent", "unknown")

    sid = await SessionService(uow).get_session_id_by_ip_user_agent(ip, device)
    if not sid:
        return None
    await redis_service.reset_chat(sid)
    await redis_service.set_session_status(sid, "chating")
    info = await redis_service.get_session_info(sid)
    return SessionInfoResponse(**info)


@audit_router.get("/session-info", response_model=SessionInfoResponse)
async def get_session_info(
    request: Request,
    redis_service: RedisCacheService = Depends(get_cache_service),
    uow: UnitOfWork = Depends(get_uow),
):
    ip = request.client.host
    device = request.headers.get("user-agent", "unknown")

    sid = await SessionService(uow).get_or_create_session_by_ip_user_agent(ip, device)
    info = await redis_service.get_session_info(sid)
    return SessionInfoResponse(**info)
