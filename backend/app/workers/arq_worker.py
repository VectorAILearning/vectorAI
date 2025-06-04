import logging
import sys

from arq.connections import RedisSettings, create_pool
from core.config import settings
from workers.audit_tasks import create_learning_task
from workers.content_tasks import generate_block_content

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)


async def on_startup(ctx):
    ctx["arq_queue"] = await create_pool(
        RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            database=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
        )
    )


async def on_shutdown(ctx):
    arq_queue = ctx["arq_queue"]
    await arq_queue.close()


class WorkerSettings:
    functions = [
        create_learning_task,
        generate_block_content,
    ]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )
    job_timeout = 200
    queue_name = "course_generation"
    on_startup = on_startup
    on_shutdown = on_shutdown
