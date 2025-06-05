import asyncio
import json
from contextlib import suppress

from core.broadcast import broadcaster
from core.config import settings
from fastapi import APIRouter, Query, WebSocket
from starlette.websockets import WebSocketState
from utils.uow import uow_context

router = APIRouter()


async def pipe_broadcast(ws: WebSocket, channel: str, sid: str):
    async with broadcaster.subscribe(channel) as sub:
        try:
            async for ev in sub:
                if ws.app.state.ws_by_sid.get(sid) is not ws:
                    break
                if ws.application_state is not WebSocketState.CONNECTED:
                    break
                await ws.send_text(ev.message)

                with suppress(json.JSONDecodeError):
                    if json.loads(ev.message).get("type") == "course_created_done":
                        break
        except asyncio.CancelledError:
            raise


@router.websocket("/ws/audit")
async def audit_websocket(ws: WebSocket, session_id: str = Query(...)):
    from services.audit_service.service import AuditDialogService
    
    old_ws = ws.app.state.ws_by_sid.get(session_id)
    if (
        old_ws
        and old_ws is not ws
        and old_ws.application_state is WebSocketState.CONNECTED
    ):
        try:
            await old_ws.send_json(
                {
                    "type": "duplicate_connection",
                    "message": "Открыта новая вкладка - это соединение будет закрыто.",
                }
            )
        except Exception:
            pass
        with suppress(Exception):
            await old_ws.close(code=4000)

    await ws.accept()
    ws.app.state.ws_by_sid[session_id] = ws

    service = AuditDialogService()

    try:
        if ws.app.state.ws_by_sid.get(session_id) is not ws:
            return
        async with uow_context() as uow:
            # TODO: получать пользователя, если у пользователя нет подписки, или пользователь
            # не авторизован и при этом уже создал курс, то закрываем соединение
            course_exist = await uow.learning_repo.get_courses_by_session_id(session_id)
            if settings.CHECK_SUBSCRIPTION and course_exist:
                # Закрываем соединение с кодом 4001, если нет подписки, но курс уже создан
                await ws.close(code=4001)
                return

        async with asyncio.TaskGroup() as tg:
            tg.create_task(service.run_dialog(ws, session_id))
            if not any(
                m.get("type") == "course_created_done"
                for m in await service.get_messages(session_id)
            ):
                tg.create_task(pipe_broadcast(ws, f"chat_{session_id}", session_id))
    finally:
        with suppress(Exception):
            if ws.app.state.ws_by_sid.get(session_id) is ws:
                ws.app.state.ws_by_sid.pop(session_id, None)
            if ws.application_state is WebSocketState.CONNECTED:
                await ws.close(code=1001)
