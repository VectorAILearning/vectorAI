from fastapi import Request
from schemas.session import SessionCreate
from services import RedisCacheService, get_cache_service
from utils.uow import UnitOfWork


class SessionService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache_service: RedisCacheService | None = None,
    ):
        self.cache_service = cache_service or get_cache_service()
        self.uow = uow

    async def get_session_id_by_ip_user_agent(
        self, ip: str, user_agent: str
    ) -> str | None:
        session_redis = await self.cache_service.get_session_id_by_ip_device(
            ip, user_agent
        )
        if session_redis:
            return session_redis

        session_db = await self.uow.session_repo.get_by_ip_user_agent(ip, user_agent)
        if session_db:
            await self.cache_service.set_session_id_for_ip_device(
                ip, user_agent, str(session_db.id)
            )
            return str(session_db.id)

        return None

    async def get_or_create_session_by_ip_user_agent(self, ip, user_agent):
        session_redis = await self.cache_service.get_session_id_by_ip_device(
            ip, user_agent
        )
        session_db = await self.uow.session_repo.get_by_ip_user_agent(ip, user_agent)

        if session_redis and session_db:
            return str(session_db.id)

        if not session_db:
            session_db = await self.uow.session_repo.create(
                SessionCreate(ip=ip, user_agent=user_agent)
            )

        if not session_redis:
            await self.cache_service.create_session(
                str(session_db.id),
                ip,
                user_agent,
            )
        return str(session_db.id)

    async def get_session_id_by_request(self, request: Request) -> str | None:
        ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        return await self.get_session_id_by_ip_user_agent(ip, user_agent)
