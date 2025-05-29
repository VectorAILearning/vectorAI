from fastapi import APIRouter
from schemas.audit import ResetChatRequest
from services import get_cache_service

audit_router = APIRouter(prefix="/audit")


@audit_router.post("/reset-chat")
async def reset_chat(body: ResetChatRequest):
    redis_service = get_cache_service()
    await redis_service.clear_messages(str(body.session_id))
    await redis_service.increment_reset_count(str(body.session_id))
    return {"status": "ok"}
