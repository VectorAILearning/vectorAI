# workers/pipeline.py
import logging
import time
import uuid

from core.config import settings
from services.audit_service.service import AuditDialogService
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.redis_cache_service import RedisCacheService
from utils.uow import uow_context

log = logging.getLogger(__name__)


def _msg(who: str, text: str, type_: str = "chat") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "ts": time.time(),
        "who": who,
        "text": text,
        "type": type_,
    }


async def create_learning_task(_, sid: str, history: str):
    """
    ARQ job: на базе истории аудита создать предпочтение пользователя и курс.
    Весь цикл работает с БД через безопасные контексты, поэтому
    ни одно соединение не «зависнет».
    """
    log.info("pipeline start %s", sid)
    redis = RedisCacheService(settings.REDIS_URL)
    if await redis.is_course_generation_in_progress(sid):
        log.info(
            f"Генерация курса уже идёт для sid={sid}, повторный запуск не требуется."
        )
        return
    await redis.set_course_generation_in_progress(sid)
    try:
        await push_and_publish(sid, _msg("bot", "Анализируем ваши предпочтения…"))

        async with uow_context() as uow:
            user_pref = await AuditDialogService(
                uow
            ).create_user_preference_by_audit_history(history, sid=sid)

            await push_and_publish(
                sid,
                _msg(
                    "system",
                    f"Предпочтение пользователя: {user_pref.summary}",
                    "system",
                ),
            )
            await push_and_publish(
                sid, _msg("bot", "Собираем для вас индивидуальный курс…")
            )

            course = await LearningService(uow).create_course_by_user_preference(
                user_pref, sid=sid
            )

            if hasattr(course, "model_dump"):
                course_data = course.model_dump()
            elif hasattr(course, "dict"):
                course_data = course.dict()
            elif hasattr(course, "__dict__"):
                course_data = course.__dict__
            else:
                raise TypeError("Unsupported course object for serialization")
            await redis.add_generated_course(sid, course_data)

            await push_and_publish(
                sid,
                _msg("bot", f"Курс «{course.title}» готов! Ознакомьтесь с деталями."),
            )
            await push_and_publish(
                sid, _msg("system", "Курс создан", "course_created_done")
            )

            await redis.set_session_status(sid, "course_created")

            log.info("pipeline done %s", sid)
    finally:
        await redis.clear_course_generation_in_progress(sid)
