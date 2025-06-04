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


async def create_learning_task(ctx, sid: str, history: str):
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

            first_lesson = None
            if course.modules and len(course.modules) > 0:
                first_module = course.modules[0]
                if first_module.lessons and len(first_module.lessons) > 0:
                    first_lesson = first_module.lessons[0]

            if first_lesson:
                await push_and_publish(
                    sid, _msg("bot", "Генерируем план для первого урока курса…")
                )
                content_list = await LearningService(
                    uow
                ).generate_and_save_lesson_content_plan(first_lesson, user_pref.summary)
                await push_and_publish(
                    sid, _msg("bot", "План первого урока сгенерирован!")
                )

                await push_and_publish(
                    sid, _msg("bot", "Генерируем контент для первого урока курса…")
                )
                if content_list:
                    first_block = min(content_list, key=lambda b: b.position)
                    await ctx["arq_queue"].enqueue_job(
                        "generate_block_content",
                        block_id=str(first_block.id),
                        lesson_id=str(first_lesson.id),
                        _queue_name="course_generation",
                    )
                await push_and_publish(
                    sid,
                    _msg("bot", "Контент первого урока будет сгенерирован поэтапно!"),
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
    except Exception as e:
        log.exception(f"Ошибка при генерации курса для sid={sid}: {e}")
        await push_and_publish(
            sid,
            _msg("bot", f"Произошла ошибка при создании курса: {str(e)}", "error"),
        )
        await push_and_publish(
            sid,
            _msg("system", "Ошибка при создании курса", "course_creation_error"),
        )
    finally:
        await redis.clear_course_generation_in_progress(sid)
