import asyncio
import json
import logging
from contextlib import suppress

from core.broadcast import broadcaster
from core.config import settings
from fastapi import APIRouter, HTTPException, Query, WebSocket
from services import get_cache_service
from utils.auth_utils import decode_access_token
from utils.uow import uow_context

router = APIRouter()

log = logging.getLogger(__name__)


async def pipe_broadcast(ws: WebSocket, channel: str, sid: str):
    async with broadcaster.subscribe(channel) as sub:
        try:
            async for ev in sub:  # type: ignore
                try:
                    await ws.send_text(ev.message)
                except Exception as e:
                    log.warning(f"Ошибка при отправке сообщения по ws: {e}")
                    break
                log.info(ev.message)
                log.info(json.loads(ev.message).get("type"))
                log.info(json.loads(ev.message).get("text") == "course_generation_done")
                if json.loads(ev.message).get("type") in [
                    "course_generation_done",
                    "course_generation_error",
                ]:
                    log.info(f"broadcast_task down for sid={sid}")
                    break
        except asyncio.CancelledError:
            log.info(f"pipe_broadcast cancelled for sid={sid}")
            raise


@router.websocket("/ws/audit")
async def audit_websocket(ws: WebSocket, token: str = Query(None)):
    from services.audit_service.service import AuditDialogService

    cache_service = get_cache_service()
    user_id = None

    async with uow_context() as uow:
        if token:
            token_payload = decode_access_token(token)
            if token_payload:
                email = token_payload.get("sub")
                if not email:
                    await ws.close(code=1008)
                    return

                user = await uow.auth_repo.get_by_email(email)
                if not user:
                    await ws.close(code=1008)
                    return
                user_id = str(user.id)
            else:
                await ws.close(code=1008)
                return

    sid = ws.cookies.get("session_id")
    if not sid or not await cache_service.get_session_by_id(sid):
        await ws.close(code=1008)
        return

    try:
        async with uow_context() as uow:
            await ws.accept()
            # TODO: получать пользователя, если у пользователя нет подписки, или пользователь
            # не авторизован и при этом уже создал курс, то закрываем соединение
            course_exist = await uow.learning_repo.get_courses_by_session_id(sid)
            if settings.CHECK_SUBSCRIPTION and course_exist:
                await ws.close(code=4001)
                return

        cache_service = get_cache_service()
        session_status = await cache_service.get_session_status(sid)
        log.info(f"session_status: {session_status}")
        broadcast_task = None
        if session_status not in ["course_generation_done", "course_generation_error"]:
            broadcast_task = asyncio.create_task(pipe_broadcast(ws, f"chat_{sid}", sid))
        if session_status == "chating":
            await AuditDialogService().run_dialog(ws, sid, user_id)
        if broadcast_task:
            await broadcast_task
    except Exception as e:
        if broadcast_task:
            broadcast_task.cancel()
            with suppress(asyncio.CancelledError):
                await broadcast_task
        log.exception(f"Error in audit_websocket: {e}")
        await ws.close(code=1001)
