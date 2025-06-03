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

            course_data = {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "estimated_time_hours": course.estimated_time_hours,
            }
            await redis.add_generated_course(sid, course_data)

            # Генерируем контент для первого урока первого модуля
            first_lesson = None
            if course.modules and len(course.modules) > 0:
                first_module = course.modules[0]
                if first_module.lessons and len(first_module.lessons) > 0:
                    first_lesson = first_module.lessons[0]
            if first_lesson:
                await push_and_publish(
                    sid, _msg("bot", "Генерируем контент для первого урока курса…")
                )
                await LearningService(uow).generate_and_save_lesson_content(
                    first_lesson, user_pref.summary
                )
                await push_and_publish(
                    sid, _msg("bot", "Контент для первого урока сгенерирован!")
                )

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


async def generate_lesson_content_task(_, lesson_id: str, user_pref: str = ""):
    async with uow_context() as uow:
        service = LearningService(uow)
        lesson = await service.get_lesson_by_id(uuid.UUID(lesson_id))
        if not lesson:
            return
        await service.generate_and_save_lesson_content(lesson, user_pref)


async def finish_course_task(_, course_id: str):
    async with uow_context() as uow:
        service = LearningService(uow)
        course = await service.get_course_by_id(uuid.UUID(course_id))
        if not course:
            return
        from agents.finishing_agent.agent import FinishingAgent

        agent = FinishingAgent()
        summary = agent.finish_course(course.description)
        log.info("Finishing course %s", course_id)
        await push_and_publish(course.session_id or "", _msg("bot", summary))
