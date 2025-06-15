import logging

from schemas import SessionInfoResponse
from services import RedisCacheService, get_cache_service
from utils.uow import UnitOfWork

log = logging.getLogger(__name__)


class SessionService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache_service: RedisCacheService | None = None,
    ):
        self.cache_service = cache_service or get_cache_service()
        self.uow = uow

    async def create_session(self) -> dict:
        session_db = await self.uow.session_repo.create()
        return await self.cache_service.create_session(str(session_db.id))

    async def check_session(self, session_id: str) -> dict | None:
        return await self.cache_service.get_session_by_id(session_id)

    async def attach_user(self, sid: str, user_id: str):
        return await self.cache_service.attach_user(sid, user_id)