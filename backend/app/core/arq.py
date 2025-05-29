from arq import create_pool
from arq.connections import RedisSettings
from core.config import settings


async def get_arq_pool():
    return await create_pool(
        RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            database=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
        )
    )
