"""
Базовый репозиторий с чистой архитектурой.
Использует кастомные исключения вместо HTTP-специфичных ошибок.
"""

from typing import Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID

from core.exceptions import DatabaseError, NotFoundError
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Базовый репозиторий для работы с моделями данных.
    Предоставляет основные CRUD операции с правильной обработкой исключений.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Инициализация репозитория.

        Args:
            session: Асинхронная сессия SQLAlchemy
            model: Модель SQLAlchemy для работы
        """
        self.session = session
        self.model = model

    async def get_by_id(self, ident: int | str | UUID) -> Optional[T]:
        """
        Получает объект по ID. Возвращает None если не найден.

        Args:
            ident: Идентификатор объекта

        Returns:
            Объект или None
        """
        try:
            return await self.session.get(self.model, ident)
        except Exception as e:
            raise DatabaseError(f"Ошибка при получении {self.model.__name__} по ID", e)

    async def get_by_id_or_raise(self, ident: int | str | UUID) -> T:
        """
        Получает объект по ID или поднимает NotFoundError.

        Args:
            ident: Идентификатор объекта

        Returns:
            Объект

        Raises:
            NotFoundError: Если объект не найден
        """
        instance = await self.get_by_id(ident)
        if instance is None:
            raise NotFoundError(self.model.__name__, ident)
        return instance

    async def get_by_ids(self, idents: Sequence[int | str | UUID]) -> list[T]:
        """
        Получает объекты по списку ID.

        Args:
            idents: Список идентификаторов

        Returns:
            Список найденных объектов
        """
        try:
            # Используем getattr для получения атрибута id
            id_attr = getattr(self.model, "id", None)
            if id_attr is None:
                raise DatabaseError(
                    f"Модель {self.model.__name__} не имеет атрибута 'id'"
                )

            result = await self.session.execute(
                select(self.model).where(id_attr.in_(idents))
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(
                f"Ошибка при получении {self.model.__name__} по списку ID", e
            )

    async def save(self, instance: T) -> T:
        """
        Сохраняет объект в БД.

        Args:
            instance: Объект для сохранения

        Returns:
            Сохраненный объект
        """
        try:
            self.session.add(instance)
            return instance
        except Exception as e:
            raise DatabaseError(f"Ошибка при сохранении {self.model.__name__}", e)

    async def delete(self, instance: T) -> None:
        """
        Удаляет объект из БД.

        Args:
            instance: Объект для удаления
        """
        try:
            await self.session.delete(instance)
        except Exception as e:
            raise DatabaseError(f"Ошибка при удалении {self.model.__name__}", e)

    async def list(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[T]:
        """
        Получает список всех объектов с опциональной пагинацией.

        Args:
            limit: Максимальное количество объектов
            offset: Смещение

        Returns:
            Список объектов
        """
        try:
            query = select(self.model)
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Ошибка при получении списка {self.model.__name__}", e)

    @staticmethod
    def apply_offset_and_limit(query: Select, offset: int, limit: int) -> Select:
        """
        Применяет пагинацию к запросу.

        Args:
            query: SQL запрос
            offset: Смещение
            limit: Лимит

        Returns:
            Запрос с пагинацией
        """
        return query.offset(offset).limit(limit)
