from typing import AsyncGenerator, Self

from core.config import settings
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatabaseHelper:
    def __init__(
        self: Self,
        url: URL,
        echo: bool = False,
        echo_pool: bool = False,
        max_overflow: int = 10,
        pool_size: int = 5,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            max_overflow=max_overflow,
            pool_size=pool_size,
            future=True,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def get_session(self: Self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


if settings.POSTGRES_URL is None:
    raise ValueError("POSTGRES_URL не может быть None")

db_helper = DatabaseHelper(url=settings.POSTGRES_URL)
