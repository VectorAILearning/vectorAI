import uuid

from fastapi import HTTPException
from models import ContentModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


class ContentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_content_by_lesson_id(
        self, lesson_id: uuid.UUID
    ) -> list[ContentModel]:
        stmt = select(ContentModel).where(ContentModel.lesson_id == lesson_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_content(self, content: ContentModel) -> ContentModel:
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)
        return content

    async def delete_content(self, content_id: uuid.UUID) -> None:
        stmt = delete(ContentModel).where(ContentModel.id == content_id)
        await self.db.execute(stmt)
        await self.db.commit()
