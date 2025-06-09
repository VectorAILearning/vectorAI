import json
import time
import uuid

from core.broadcast import broadcaster
from pydantic import BaseModel, Field
from services import get_cache_service

redis = get_cache_service()


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    who: str
    text: str
    ts: float = Field(default_factory=lambda: time.time())


async def push_and_publish(
    msg: dict | ChatMessage, session_id: str | uuid.UUID | None = None
) -> ChatMessage | None:
    """
    Сохраняем сообщение в Redis-историю.
    Публикуем его в канал broadcaster.
    Возвращаем нормализованный ChatMessage (можно использовать дальше).
    Если session_id не передан, то сообщение не сохраняется в Redis-историю и не публикуется в канал broadcaster.
    """
    if session_id:
        if isinstance(msg, dict):
            msg_obj = ChatMessage(**msg)
        else:
            msg_obj = msg

        data = msg_obj.model_dump()

        await redis.add_message(str(session_id), data)

        await broadcaster.publish(
            f"chat_{session_id}",
            json.dumps(data, ensure_ascii=False),
        )

        return msg_obj
    return None
