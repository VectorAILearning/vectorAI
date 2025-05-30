import asyncio, json, uuid
from contextlib import suppress

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketState

from core.broadcast import broadcaster
from services import get_cache_service
from services.audit_service import AuditDialogService

router = APIRouter()


async def pipe_broadcast(ws: WebSocket, channel: str):
    try:
        async with broadcaster.subscribe(channel) as sub:
            async for ev in sub:
                if ws.application_state is not WebSocketState.CONNECTED:
                    break
                await ws.send_text(ev.message)
                with suppress(json.JSONDecodeError):
                    if json.loads(ev.message).get("type") == "course_created_done":
                        break
    except asyncio.CancelledError:
        pass


@router.websocket("/ws/audit")
async def audit_websocket(ws: WebSocket):
    await ws.accept()

    redis = get_cache_service()
    ip = ws.client.host
    device = ws.headers.get("user-agent", "unknown")
    sid = (
        ws.query_params.get("session_id")
        or await redis.get_session_id_by_ip_device(ip, device)
        or str(uuid.uuid4())
    )

    await redis.set_session_id_for_ip_device(ip, device, sid)
    if not await redis.session_exists(sid):
        await redis.create_session(sid, ip, device)

    course_ready = any(
        m.get("type") == "course_created_done" for m in await redis.get_messages(sid)
    )

    dialog = AuditDialogService(ws, redis, sid)

    try:
        await dialog.send_session_info()
        async with asyncio.TaskGroup() as tg:
            tg.create_task(dialog.run_dialog())
            if not course_ready:
                tg.create_task(pipe_broadcast(ws, f"chat_{sid}"))
    finally:
        with suppress(Exception):
            if ws.application_state is WebSocketState.CONNECTED:
                await ws.close()
