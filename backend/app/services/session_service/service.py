from core.database import db_helper
from schemas.session import SessionCreate
from services import get_cache_service
from utils.uow import UnitOfWork


class SessionService:
    def __init__(self, redis_service, uow: UnitOfWork):
        self.redis_service = redis_service
        self.uow = uow

    async def get_session_db_by_id(self):
        pass

    async def get_or_create_session_by_ip_user_agent(self, ip, user_agent):
        sid = await self.redis_service.get_session_id_by_ip_device(ip, user_agent)
        if not sid:
            sid = str(
                (
                    await self.uow.session_repo.create(
                        SessionCreate(ip=ip, user_agent=user_agent)
                    )
                ).id
            )
            await self.redis_service.set_session_id_for_ip_device(ip, user_agent, sid)
            if not await self.redis_service.session_exists(sid):
                await self.redis_service.create_session(sid, ip, user_agent)

        return sid


async def get_session_service() -> SessionService:
    redis_service = get_cache_service()

    async with db_helper.session_factory() as session:
        uow = UnitOfWork(session=session)
        return SessionService(redis_service=redis_service, uow=uow)
