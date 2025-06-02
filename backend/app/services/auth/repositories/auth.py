from models.base import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalars().first()
