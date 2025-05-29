from core.config import settings

from .redis_cache_service import RedisCacheService


def get_cache_service():
    return RedisCacheService(settings.REDIS_URL)
