from fastapi import APIRouter, Depends, Request
from services import RedisCacheService, get_cache_service
from services.session_service.service import SessionService
from utils.uow import UnitOfWork, get_uow

audit_router = APIRouter(prefix="/audit")


@audit_router.post("/reset-chat")
async def reset_chat(
    request: Request,
    redis_service: RedisCacheService = Depends(get_cache_service),
    uow: UnitOfWork = Depends(get_uow),
):
    ip = request.client.host
    device = request.headers.get("user-agent", "unknown")

    sid = await SessionService(uow).get_or_create_session_by_ip_user_agent(ip, device)
    return await redis_service.reset_chat(sid)
