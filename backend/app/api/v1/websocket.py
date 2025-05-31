import asyncio
import json
from contextlib import suppress

from core.broadcast import broadcaster
from fastapi import APIRouter, Depends, WebSocket
from services.audit_service.service import AuditDialogService, get_audit_service
from services.session_service.service import SessionService, get_session_service
from starlette.websockets import WebSocketState

router = APIRouter()


async def pipe_broadcast(ws: WebSocket, channel: str):
    async with broadcaster.subscribe(channel) as sub:
        try:
            async for ev in sub:
                if ws.application_state is not WebSocketState.CONNECTED:
                    break
                await ws.send_text(ev.message)

                with suppress(json.JSONDecodeError):
                    if json.loads(ev.message).get("type") == "course_created_done":
                        break
        except asyncio.CancelledError:
            raise


@router.websocket("/ws/audit")
async def audit_websocket(
    ws: WebSocket,
    session_service: SessionService = Depends(get_session_service),
    audit_service: AuditDialogService = Depends(get_audit_service),
):
    await ws.accept()

    ip = ws.client.host
    device = ws.headers.get("user-agent", "unknown")
    sid = ws.query_params.get(
        "session_id"
    ) or await session_service.get_or_create_session_by_ip_user_agent(ip, device)

    try:
        await audit_service.send_session_info(ws, sid)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(audit_service.run_dialog(ws, sid))
            if not any(
                m.get("type") == "course_created_done"
                for m in await audit_service.get_messages(sid)
            ):
                tg.create_task(pipe_broadcast(ws, f"chat_{sid}"))
    finally:
        with suppress(Exception):
            if ws.application_state is WebSocketState.CONNECTED:
                await ws.close(code=1001)
