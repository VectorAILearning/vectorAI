from schemas.session import SessionCreate
from services import get_cache_service, RedisCacheService
from utils.uow import UnitOfWork


class SessionService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache_service: RedisCacheService | None = None,
    ):
        self.cache_service = cache_service or get_cache_service()
        self.uow = uow

    async def get_session_db_by_id(self):
        pass

    async def init_session_by_id(self, session_id: str, ip: str, device: str) -> str:
        redis_exist = await self.cache_service.session_exists(session_id)
        session_db = await self.uow.session_repo.get_by_id(session_id)

        if redis_exist and session_db:
            return session_db.id

        if not session_db:
            session_db = await self.uow.session_repo.create(
                SessionCreate(ip=ip, user_agent=device)
            )

        if not redis_exist:
            await self.cache_service.create_session(
                session_id,
                ip,
                device,
            )
        return session_db.id

    async def get_or_create_session_by_ip_user_agent(self, ip, user_agent):
        sid = await self.cache_service.get_session_id_by_ip_device(ip, user_agent)
        if not sid:
            sid = str(
                (
                    await self.uow.session_repo.create(
                        SessionCreate(ip=ip, user_agent=user_agent)
                    )
                ).id
            )
            await self.cache_service.set_session_id_for_ip_device(ip, user_agent, sid)
            if not await self.cache_service.session_exists(sid):
                await self.cache_service.create_session(sid, ip, user_agent)

        return sid
