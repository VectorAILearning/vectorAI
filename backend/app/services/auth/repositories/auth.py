"""
Репозиторий для работы с пользователями в контексте аутентификации.
Наследует BaseRepository и добавляет специфичные для аутентификации методы.
"""

from typing import Optional

from core.exceptions import DatabaseError
from models.base import UserModel
from services.base.repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class AuthRepository(BaseRepository[UserModel]):
    """
    Репозиторий для аутентификации пользователей.
    Предоставляет методы для поиска пользователей по email и другие auth-специфичные операции.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """
        Получает пользователя по email адресу.

        Args:
            email: Email адрес пользователя

        Returns:
            Пользователь или None если не найден

        Raises:
            DatabaseError: При ошибке запроса к БД
        """
        try:
            result = await self.session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            return result.scalars().first()
        except Exception as e:
            raise DatabaseError(f"Ошибка при поиске пользователя по email {email}", e)

    async def email_exists(self, email: str) -> bool:
        """
        Проверяет существование пользователя с данным email.

        Args:
            email: Email адрес для проверки

        Returns:
            True если пользователь существует
        """
        user = await self.get_by_email(email)
        return user is not None
