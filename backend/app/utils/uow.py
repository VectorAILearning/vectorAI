from typing import Annotated

from core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth.repository import AuthRepository
from services.audit_service.repository import AuditRepository
from services.learning_service.repository import LearningRepository
from services.session_service.repository import SessionRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_repo = AuthRepository(self.session)
        self.audit_repo = AuditRepository(self.session)
        self.learning_repo = LearningRepository(self.session)
        self.session_repo = SessionRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


async def get_uow(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> UnitOfWork:
    uow = UnitOfWork(session=session)
    return uow
