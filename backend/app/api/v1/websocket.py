import asyncio
import json
import logging
from contextlib import suppress

from core.broadcast import broadcaster
from core.config import settings
from fastapi import APIRouter, Query, WebSocket
from services import get_cache_service
from utils.uow import uow_context

router = APIRouter()

log = logging.getLogger(__name__)


async def pipe_broadcast(ws: WebSocket, channel: str, sid: str):
    async with broadcaster.subscribe(channel) as sub:
        try:
            async for ev in sub:
                await ws.send_text(ev.message)
                if json.loads(ev.message).get("type") == "course_created_done":
                    break
        except asyncio.CancelledError:
            log.info(f"pipe_broadcast cancelled for sid={sid}")
            raise


@router.websocket("/ws/audit")
async def audit_websocket(ws: WebSocket, session_id: str = Query(...)):
    from services.audit_service.service import AuditDialogService

    await ws.accept()

    try:
        async with uow_context() as uow:
            # TODO: получать пользователя, если у пользователя нет подписки, или пользователь
            # не авторизован и при этом уже создал курс, то закрываем соединение
            course_exist = await uow.learning_repo.get_courses_by_session_id(session_id)
            if settings.CHECK_SUBSCRIPTION and course_exist:
                await ws.close(code=4001)
                return

        cache_service = get_cache_service()
        session_status = await cache_service.get_session_status(session_id)
        log.info(f"session_status: {session_status}")
        if session_status != "course_created_done":
            broadcast_task = asyncio.create_task(
                pipe_broadcast(ws, f"chat_{session_id}", session_id)
            )
        if session_status == "chating":
            await AuditDialogService().run_dialog(ws, session_id)
    except Exception as e:
        if broadcast_task:
            broadcast_task.cancel()
            with suppress(asyncio.CancelledError):
                await broadcast_task
        log.exception(f"Error in audit_websocket: {e}")
        await ws.close(code=1001)
