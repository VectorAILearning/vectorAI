import uuid

from sqlalchemy import select
from fastapi import HTTPException
from models import PreferenceModel
from schemas import PreferenceUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_preference_by_session_id(
        self, session_id: str
    ) -> PreferenceModel | None:
        stmt = select(PreferenceModel).where(PreferenceModel.session_id == session_id)
        result = await self.db.execute(stmt)
        preference = result.scalar_one_or_none()
        return preference

    async def create_user_preference(
        self,
        summary: str,
        user_id: str = None,
        sid: str = None,
    ) -> PreferenceModel:
        preference = PreferenceModel(
            user_id=uuid.UUID(user_id) if user_id else None,
            session_id=uuid.UUID(sid) if sid else None,
            summary=summary,
        )
        self.db.add(preference)
        await self.db.commit()
        await self.db.refresh(preference)
        return preference

    async def update_course_preference(
        self, preference_id, data: PreferenceUpdate
    ) -> PreferenceModel:
        preference_db = await self.db.get(PreferenceModel, preference_id)
        if not preference_db:
            raise HTTPException(
                status_code=404, detail=f"Preference with {preference_id} not found"
            )

        data_dict = data.model_dump(exclude_unset=True)

        for key, value in data_dict.items():
            setattr(preference_db, key, value)

        await self.db.commit()
        await self.db.refresh(preference_db)
        return preference_db
