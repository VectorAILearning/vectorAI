import uuid

from fastapi import HTTPException
from models import SessionModel
from schemas.session import SessionCreate, SessionUpdate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, session_id: uuid.UUID) -> SessionModel | None:
        session_db = await self.db.get(SessionModel, session_id)
        return session_db

    async def get_by_ip_user_agent(
        self, ip: str, user_agent: str
    ) -> SessionModel | None:
        session_db = await self.db.execute(
            select(SessionModel).where(
                SessionModel.ip == ip, SessionModel.user_agent == user_agent
            )
        )
        return session_db.scalar_one_or_none()

    async def create(self, session_data: SessionCreate) -> SessionModel:
        session = SessionModel(**session_data.model_dump())
        self.db.add(session)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()

            stmt = select(SessionModel).where(
                SessionModel.ip == session_data.ip,
                SessionModel.user_agent == session_data.user_agent,
            )
            session = (await self.db.execute(stmt)).scalar_one()
        await self.db.refresh(session)
        return session

    async def update(
        self,
        session_id: uuid.UUID,
        data: SessionUpdate,
    ):
        db_session = await self.db.get(SessionModel, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        data_dict = data.model_dump(exclude_unset=True)

        for key, value in data_dict.items():
            setattr(db_session, key, value)

        await self.db.commit()
        await self.db.refresh(db_session)
        return db_session

    async def switch_to_new(self, old_session: SessionModel) -> uuid.UUID:
        new_session = SessionModel(
            ip=old_session.ip,
            user_agent=old_session.user_agent,
        )
        self.db.add(new_session)

        old_session.user_id = None

        await self.db.commit()
        await self.db.refresh(new_session)
        return new_session.id
