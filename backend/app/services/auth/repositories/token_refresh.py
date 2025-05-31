import uuid
from datetime import datetime, timezone

from models import RefreshTokenModel
from services.base.repository import BaseRepository
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class RefreshTokenRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshTokenModel)
        self.session = session

    async def get_by_token(self, token: str) -> RefreshTokenModel | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token_id: uuid.UUID) -> bool:
        token = await self.get_by_id(ident=token_id)
        if token and not token.revoked:
            token.revoked = True
            return True
        return False

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked == False,
                RefreshTokenModel.expires_at
                > datetime.now(timezone.utc),  # Используем UTC
            )
            .values(revoked=True)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def delete_by_id(self, token_id: uuid.UUID) -> bool:
        token = await self.get_by_id(ident=token_id)
        if token:
            await self.session.delete(token)
            return True
        return False
