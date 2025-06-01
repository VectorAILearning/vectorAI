import asyncio
import json
from contextlib import suppress

from core.broadcast import broadcaster
from fastapi import APIRouter, WebSocket
from services.audit_service.service import AuditDialogService
from services.session_service.service import SessionService
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
async def audit_websocket(ws: WebSocket):
    ip = ws.client.host
    device = ws.headers.get("user-agent", "unknown")

    async with uow_context() as uow:
        sid = await SessionService(uow).get_or_create_session_by_ip_user_agent(
            ip, device
        )

    old_ws = ws.app.state.ws_by_sid.get(sid)
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
    ws.app.state.ws_by_sid[sid] = ws

    service = AuditDialogService()

    try:
        if ws.app.state.ws_by_sid.get(sid) is not ws:
            return
        await service.send_session_info(ws, sid)
        async with uow_context() as uow:
            course_exist = await uow.learning_repo.get_course_by_session_id(sid)
            if course_exist:
                await ws.close(code=1000)
                return

        async with asyncio.TaskGroup() as tg:
            tg.create_task(service.run_dialog(ws, sid))
            if not any(
                m.get("type") == "course_created_done"
                for m in await service.get_messages(sid)
            ):
                tg.create_task(pipe_broadcast(ws, f"chat_{sid}", sid))
    finally:
        with suppress(Exception):
            if ws.app.state.ws_by_sid.get(sid) is ws:
                ws.app.state.ws_by_sid.pop(sid, None)
            if ws.application_state is WebSocketState.CONNECTED:
                await ws.close(code=1001)
