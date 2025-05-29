from arq.connections import RedisSettings
from core.config import settings
from workers.audit_tasks import audit_full_pipeline_task


class WorkerSettings:
    functions = [audit_full_pipeline_task]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )
    job_timeout = 200
