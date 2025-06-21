"""
Репозиторий для работы с refresh токенами.
Наследует BaseRepository и добавляет специфичные для токенов методы.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from core.exceptions import DatabaseError, NotFoundError
from models import RefreshTokenModel
from services.base.repository import BaseRepository
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class RefreshTokenRepository(BaseRepository[RefreshTokenModel]):
    """
    Репозиторий для управления refresh токенами.
    Предоставляет методы для поиска, отзыва и управления токенами.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshTokenModel)

    async def get_by_token(self, token: str) -> Optional[RefreshTokenModel]:
        """
        Получает refresh токен по строковому значению.

        Args:
            token: Строковое значение токена

        Returns:
            RefreshTokenModel или None если не найден

        Raises:
            DatabaseError: При ошибке запроса к БД
        """
        try:
            stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseError(f"Ошибка при поиске токена", e)

    async def revoke(self, token_id: uuid.UUID) -> bool:
        """
        Отзывает refresh токен по ID.

        Args:
            token_id: ID токена для отзыва

        Returns:
            True если токен был успешно отозван

        Raises:
            NotFoundError: Если токен не найден
            DatabaseError: При ошибке БД
        """
        try:
            token = await self.get_by_id_or_raise(token_id)
            if not token.revoked:
                token.revoked = True
                return True
            return False
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка при отзыве токена {token_id}", e)

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        """
        Отзывает все активные токены пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Количество отозванных токенов

        Raises:
            DatabaseError: При ошибке БД
        """
        try:
            stmt = (
                update(RefreshTokenModel)
                .where(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.revoked == False,
                    RefreshTokenModel.expires_at > datetime.now(timezone.utc),
                )
                .values(revoked=True)
                .execution_options(synchronize_session="fetch")
            )
            result = await self.session.execute(stmt)
            return result.rowcount or 0
        except Exception as e:
            raise DatabaseError(f"Ошибка при отзыве токенов пользователя {user_id}", e)

    async def delete_by_id(self, token_id: uuid.UUID) -> bool:
        """
        Удаляет токен по ID.

        Args:
            token_id: ID токена для удаления

        Returns:
            True если токен был удален

        Raises:
            DatabaseError: При ошибке БД
        """
        try:
            token = await self.get_by_id(token_id)
            if token:
                await self.delete(token)
                return True
            return False
        except Exception as e:
            raise DatabaseError(f"Ошибка при удалении токена {token_id}", e)
