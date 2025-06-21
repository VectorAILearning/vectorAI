"""
Фабрика сервисов для создания всех сервисов с их зависимостями.
Содержит всю логику создания сервисов в одном месте.
"""

from services.auth.repositories.auth import AuthRepository
from services.auth.repositories.token_refresh import RefreshTokenRepository
from services.auth.service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession


class ServiceFactory:
    """
    Фабрика для создания всех сервисов приложения.
    Централизует логику создания сервисов и их зависимостей.
    """

    @staticmethod
    def create_auth_service(session: AsyncSession) -> AuthService:
        """
        Создает сервис аутентификации со всеми зависимостями.

        Args:
            session: Асинхронная сессия БД

        Returns:
            Настроенный AuthService
        """
        auth_repo = AuthRepository(session)
        refresh_token_repo = RefreshTokenRepository(session)

        return AuthService(
            session=session, auth_repo=auth_repo, refresh_token_repo=refresh_token_repo
        )
