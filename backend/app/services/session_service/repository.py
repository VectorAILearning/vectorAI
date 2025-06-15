import uuid

from models import SessionModel
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, session_id: uuid.UUID) -> SessionModel | None:
        session_db = await self.db.get(SessionModel, session_id)
        return session_db

    async def create(self) -> SessionModel:
        session = SessionModel()
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
