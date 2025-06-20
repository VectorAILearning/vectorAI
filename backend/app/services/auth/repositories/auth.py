from models.base import UserModel
from services.base.repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class AuthRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalars().first()
