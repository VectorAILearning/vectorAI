import asyncio
import json
import uuid
from contextlib import suppress

from core.broadcast import broadcaster
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services import get_cache_service
from services.audit_service import AuditDialogService
from starlette.websockets import WebSocketState

websocket_router = APIRouter()


async def wait_course_done(ws: WebSocket, channel: str, done: asyncio.Event) -> None:
    """Проксируем сообщения из broadcaster в WebSocket.
    Выходим, если:
    * соединение закрыто;
    * получен CancelledError (reload/shutdown);
    * поймано событие `course_created_done` (ставим done.set()).
    """
    try:
        async with broadcaster.subscribe(channel) as sub:
            async for ev in sub:
                if ws.application_state is not WebSocketState.CONNECTED:
                    break

                try:
                    await ws.send_text(ev.message)
                except RuntimeError:
                    break

                with suppress(json.JSONDecodeError):
                    if json.loads(ev.message).get("type") == "course_created_done":
                        done.set()
                        return
    except asyncio.CancelledError:
        raise


@websocket_router.websocket("/ws/audit")
async def audit_websocket(ws: WebSocket):
    """Основной WebSocket‑обработчик аудита.

    * Если курс **уже** создан (в Redis есть сообщение `course_created_done`),
      не создаём таск‑слушатель и сразу завершаем работу после диалога.
    * Иначе запускаем `wait_course_done`, ждём событие или 10‑секундный тайм‑аут,
      чтобы не вешать процесс при hot‑reload.
    """
    await ws.accept()

    redis = get_cache_service()
    ip = ws.client.host
    device = ws.headers.get("user-agent", "unknown")
    session_id = ws.query_params.get(
        "session_id"
    ) or await redis.get_session_id_by_ip_device(ip, device)

    if not session_id:
        session_id = str(uuid.uuid4())
        await redis.set_session_id_for_ip_device(ip, device, session_id)
        await redis.create_session(session_id, ip, device)

    # Проверяем, не создан ли курс уже раньше
    existing_messages = await redis.get_messages(session_id)
    course_already_created = any(
        m.get("type") == "course_created_done" for m in (existing_messages or [])
    )

    dialog = AuditDialogService(ws, redis, session_id)

    listener_task: asyncio.Task | None = None
    course_done_evt: asyncio.Event | None = None

    if not course_already_created:
        course_done_evt = asyncio.Event()
        listener_task = asyncio.create_task(
            wait_course_done(ws, f"chat_{session_id}", course_done_evt)
        )

    try:
        await dialog.send_session_info()
        await dialog.run_dialog()

        if course_done_evt is not None:
            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(course_done_evt.wait(), timeout=10)
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        if listener_task is not None:
            listener_task.cancel()
            with suppress(asyncio.CancelledError):
                await listener_task

        with suppress(Exception):
            await ws.close()
