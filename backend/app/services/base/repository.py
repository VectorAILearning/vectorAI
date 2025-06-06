from typing import List, Optional, Sequence, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Result, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")


class BaseRepository:
    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        :param session: Асинхронная сессия SQLAlchemy.
        :param model: Модель SQLAlchemy, с которой работает репозиторий.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, ident: int | str | UUID) -> Optional[T]:
        instance: Optional[T] = await self.session.get(self.model, ident)
        if instance is None:
            raise HTTPException(
                detail=f"Объект {self.model.__name__} с ID {ident} не найден.",
                status_code=404,
            )
        return instance

    async def get_by_ids(self, idents: Sequence[int | str]) -> list[Result]:
        instances = await self.session.execute(
            select(self.model).where(self.model.id.in_(idents))
        )
        results = instances.scalars().all()
        return results

    async def save(self, instance: T) -> T:
        self.session.add(instance)
        return instance

    async def delete(self, instance: T):
        await self.session.delete(instance)

    async def list(self) -> list[T]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    @staticmethod
    def apply_offset_and_limit(query: Select, offset: int, limit: int) -> Select:
        return query.offset(offset).limit(limit)
