import json, uuid
import time

from core.broadcast import broadcaster
from services import get_cache_service
from pydantic import BaseModel, Field

redis = get_cache_service()


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    who: str
    text: str
    ts: float = Field(default_factory=lambda: time.time())


async def push_and_publish(session_id: str, msg: dict | ChatMessage) -> ChatMessage:
    """
    Сохраняем сообщение в Redis-историю.
    Публикуем его в канал broadcaster.
    Возвращаем нормализованный ChatMessage (можно использовать дальше).
    """
    if isinstance(msg, dict):
        msg_obj = ChatMessage(**msg)
    else:
        msg_obj = msg

    data = msg_obj.model_dump()

    await redis.add_message(session_id, data)

    await broadcaster.publish(
        f"chat_{session_id}",
        json.dumps(data, ensure_ascii=False),
    )

    return msg_obj
