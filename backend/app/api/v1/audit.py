from fastapi import APIRouter, Depends
from schemas.audit import ResetChatRequest
from services import RedisCacheService, get_cache_service

audit_router = APIRouter(prefix="/audit")


@audit_router.post("/reset-chat")
async def reset_chat(
    body: ResetChatRequest,
    redis_service: RedisCacheService = Depends(get_cache_service),
):
    return await redis_service.reset_chat(str(body.session_id))
