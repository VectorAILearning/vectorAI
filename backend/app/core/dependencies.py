"""
Зависимости для FastAPI с интеграцией DI контейнера.
Предоставляет dependency functions для endpoints.
"""

from typing import AsyncGenerator

from core.container import container
from core.database import db_helper
from core.service_factory import ServiceFactory
from fastapi import Depends
from services.auth.service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

container.register_factory(AuthService, ServiceFactory.create_auth_service)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии БД.
    Автоматически закрывает сессию после использования.
    """
    async with db_helper.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_container():
    """
    Dependency для получения DI контейнера.

    Returns:
        Глобальный экземпляр контейнера
    """
    return container


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    di_container=Depends(get_container),
) -> AuthService:
    """
    Dependency для получения сервиса аутентификации.

    Args:
        session: Асинхронная сессия БД
        di_container: DI контейнер

    Returns:
        Настроенный AuthService
    """
    return di_container.get_service(AuthService, session=session)
