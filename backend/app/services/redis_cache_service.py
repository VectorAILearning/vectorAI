# services/redis_cache.py
import json, logging, time, uuid
import redis.asyncio as aioredis
from core.config import settings

log = logging.getLogger(__name__)

CHAT = "chat:{sid}"
SESSION = "session:{sid}"
RESET = "reset:{sid}"


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

    async def session_exists(self, sid: str) -> bool:
        await self._conn()
        return await self._r.exists(SESSION.format(sid=sid)) == 1

    async def create_session(self, sid: str, ip: str, dev: str):
        await self._conn()
        await self._r.set(
            SESSION.format(sid=sid),
            json.dumps({"ip": ip, "device": dev}),
            ex=settings.REDIS_SESSION_TTL,
            nx=True,
        )

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

    async def get_session_id_by_ip_device(self, ip: str, dev: str):
        await self._conn()
        return await self._r.get(f"session_map:{ip}:{dev}")

    async def set_session_id_for_ip_device(self, ip: str, dev: str, sid: str):
        await self._conn()
        await self._r.set(f"session_map:{ip}:{dev}", sid, ex=settings.REDIS_SESSION_TTL)

    async def get_reset_count(self, sid: str) -> int:
        await self._conn()
        val = await self._r.get(RESET.format(sid=sid))
        return int(val) if val else 0

    async def increment_reset_count(self, sid: str) -> int:
        await self._conn()
        key = RESET.format(sid=sid)
        n = await self._r.incr(key)
        await self._r.expire(key, settings.REDIS_SESSION_TTL)
        return n

    async def get_session_info(self, sid: str):
        await self._conn()
        raw = await self._r.get(SESSION.format(sid=sid))
        return {
            "session": json.loads(raw) if raw else {},
            "reset_count": await self.get_reset_count(sid),
            "messages": await self.get_messages(sid),
        }
