from arq.connections import RedisSettings
from core.config import settings
from workers.audit_tasks import create_learning_task


class WorkerSettings:
    functions = [create_learning_task]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )
    job_timeout = 200
