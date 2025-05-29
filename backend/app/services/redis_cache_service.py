import json

import redis.asyncio as aioredis
from core.config import settings


class RedisCacheService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        if not self.redis:
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def session_exists(self, session_id: str) -> bool:
        await self.connect()
        return await self.redis.exists(session_id) > 0

    async def create_session(self, session_id: str, ip: str, device: str):
        await self.connect()
        data = {"ip": ip, "device": device, "messages": []}
        await self.redis.set(
            session_id, json.dumps(data), ex=settings.REDIS_SESSION_TTL
        )

    async def get_messages(self, session_id: str):
        await self.connect()
        data = await self.redis.get(session_id)
        if data:
            return json.loads(data).get("messages", [])
        return []

    async def add_message(self, session_id: str, message: dict):
        await self.connect()
        data = await self.redis.get(session_id)
        if data:
            obj = json.loads(data)
            obj.setdefault("messages", []).append(message)
            await self.redis.set(session_id, json.dumps(obj))
        else:
            obj = {"messages": [message]}
            await self.redis.set(session_id, json.dumps(obj))

    async def get_session_id_by_ip_device(self, ip: str, device: str) -> str | None:
        await self.connect()
        key = f"session_map:{ip}:{device}"
        return await self.redis.get(key)

    async def set_session_id_for_ip_device(self, ip: str, device: str, session_id: str):
        await self.connect()
        key = f"session_map:{ip}:{device}"
        await self.redis.set(key, session_id, ex=settings.REDIS_SESSION_TTL)

    async def get_reset_count(self, session_id: str) -> int:
        await self.connect()
        key = f"reset_count:{session_id}"
        value = await self.redis.get(key)
        return int(value) if value is not None else 0

    async def increment_reset_count(self, session_id: str):
        await self.connect()
        key = f"reset_count:{session_id}"
        count = await self.redis.incr(key)
        await self.redis.expire(key, settings.REDIS_SESSION_TTL)
        return count

    async def clear_messages(self, session_id: str):
        await self.connect()
        data = await self.redis.get(session_id)
        if data:
            obj = json.loads(data)
            obj["messages"] = []
            await self.redis.set(
                session_id, json.dumps(obj), ex=settings.REDIS_SESSION_TTL
            )

    async def get_session_info(self, session_id: str):
        await self.connect()
        data = await self.redis.get(session_id)
        reset_count = await self.get_reset_count(session_id)
        return {"session": json.loads(data) if data else {}, "reset_count": reset_count}
