import json
import logging
import time
import uuid
from datetime import datetime

import redis.asyncio as aioredis
from core.config import settings

log = logging.getLogger(__name__)

CHAT = "chat:{sid}"
SESSION = "session:{sid}"
RESET = "reset:{sid}"
COURSE_GEN = "course_generation:{sid}"
SESSION_STATUS = "session_status:{sid}"
GENERATED_COURSES = "generated_courses:{sid}"


class RedisCacheService:
    def __init__(self, url: str):
        self._url = url
        self._r = None

    async def _conn(self):
        if not self._r:
            self._r = aioredis.from_url(self._url, decode_responses=True)

    async def close(self):
        if self._r:
            await self._r.close()
            self._r = None

    async def create_session(self, sid: str) -> dict:
        await self._conn()
        await self._r.set(
            SESSION.format(sid=sid),
            json.dumps({"user_id": "", "created_at": datetime.now().isoformat()}),
            ex=settings.SESSION_TTL,
            nx=True,
        )
        return await self.get_session_info(sid)

    async def get_messages(self, sid: str):
        await self._conn()
        raw = await self._r.lrange(CHAT.format(sid=sid), 0, -1)
        return [json.loads(x) for x in raw]

    async def add_message(self, sid: str, msg: dict):
        await self._conn()
        msg.setdefault("id", str(uuid.uuid4()))
        msg.setdefault("ts", time.time())
        await self._r.rpush(CHAT.format(sid=sid), json.dumps(msg))
        log.debug("saved %s for %s", msg["id"], sid)

    async def clear_messages(self, sid: str):
        await self._conn()
        await self._r.delete(CHAT.format(sid=sid))

    async def get_session_by_id(self, sid: str) -> dict | None:
        await self._conn()
        return await self._r.get(SESSION.format(sid=sid))

    async def get_reset_count(self, sid: str) -> int:
        await self._conn()
        val = await self._r.get(RESET.format(sid=sid))
        return int(val) if val else 0

    async def reset_chat(self, sid: str):
        await self.clear_messages(sid)
        await self.increment_reset_count(sid)
        return {"status": "ok"}

    async def increment_reset_count(self, sid: str) -> int:
        await self._conn()
        key = RESET.format(sid=sid)
        n = await self._r.incr(key)
        await self._r.expire(key, settings.SESSION_TTL)
        return n

    async def get_session_info(self, sid: str) -> dict | None:
        await self._conn()
        raw = await self._r.get(SESSION.format(sid=sid))

        if not raw:
            return None

        return {
            "session_id": sid,
            "session": json.loads(raw),
            "reset_count": await self.get_reset_count(sid),
            "messages": await self.get_messages(sid),
            "status": await self.get_session_status(sid),
            "generated_courses": await self.get_generated_courses(sid),
        }

    async def set_course_generation_in_progress(self, sid: str):
        await self._conn()
        await self._r.set(COURSE_GEN.format(sid=sid), "1", ex=settings.SESSION_TTL)

    async def is_course_generation_in_progress(self, sid: str) -> bool:
        await self._conn()
        return await self._r.exists(COURSE_GEN.format(sid=sid)) == 1

    async def clear_course_generation_in_progress(self, sid: str):
        await self._conn()
        await self._r.delete(COURSE_GEN.format(sid=sid))

    async def set_session_status(self, sid: str, status: str):
        await self._conn()
        await self._r.set(
            SESSION_STATUS.format(sid=sid), status, ex=settings.SESSION_TTL
        )

    async def get_session_status(self, sid: str) -> str:
        await self._conn()
        status = await self._r.get(SESSION_STATUS.format(sid=sid))
        return status or "chating"

    async def add_generated_course(self, sid: str, course_data: dict):
        await self._conn()
        await self._r.lpush(GENERATED_COURSES.format(sid=sid), json.dumps(course_data))
        await self._r.expire(GENERATED_COURSES.format(sid=sid), settings.SESSION_TTL)

    async def get_generated_courses(self, sid: str) -> list[dict]:
        await self._conn()
        raw_list = await self._r.lrange(GENERATED_COURSES.format(sid=sid), 0, -1)
        return [json.loads(x) for x in raw_list]

    async def attach_user(self, sid: str, user_id: str):
        await self._conn()
        key = SESSION.format(sid=sid)
        raw = await self._r.get(key)
        if not raw:
            raise ValueError("session not found")
        payload = json.loads(raw)
        payload["user_id"] = user_id
        await self._r.set(key, json.dumps(payload), ex=settings.SESSION_TTL)
