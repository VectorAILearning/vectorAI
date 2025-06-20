import logging

from core.config import settings
from fastapi import Request
from services import RedisCacheService, get_cache_service
from services.session_service.repository import SessionRepository
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


def get_session_service(session: AsyncSession) -> "SessionService":
    """
    Фабричный метод для создания SessionService
    """
    session_repo = SessionRepository(session)
    return SessionService(session, session_repo, get_cache_service())


class SessionService:
    def __init__(
        self,
        session: AsyncSession,
        session_repo: SessionRepository,
        cache_service: RedisCacheService,
    ):
        self.session = session
        self.session_repo = session_repo
        self.cache_service = cache_service

    async def create_session(self) -> dict:
        session_db = await self.session_repo.create()
        return await self.cache_service.create_session(str(session_db.id))

    async def check_session(self, session_id: str) -> dict | None:
        return await self.cache_service.get_session_by_id(session_id)

    async def attach_user(self, sid: str, user_id: str):
        return await self.cache_service.attach_user(sid, user_id)

    async def get_session_id_by_request(self, request: Request) -> str | None:
        """
        Получает session_id из куки запроса
        """
        return request.cookies.get(settings.SESSION_COOKIE_KEY)
