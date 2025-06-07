import logging

from core.config import settings
from models.course import CourseModel
from models.task import TaskTypeEnum
from schemas.course import CourseOut
from schemas.task import TaskIn
from services import get_cache_service
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from utils.uow import uow_context
from workers.generate_tasks.audit_tasks import _msg
from workers.generate_tasks.generate_tasks import GenerateDeepEnum

log = logging.getLogger(__name__)


async def generate_course_by_user_preference(
    ctx, user_pref: str, generate_tasks_context: dict
) -> CourseModel:
    """
    Генерация курса на основе предпочтений пользователя.
    Args:
        ctx: контекст
        user_pref: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        CourseModel: курс
    """
    sid = generate_tasks_context["params"].get("sid")
    user_id = generate_tasks_context["params"].get("user_id")
    generate_params = generate_tasks_context["params"]
    generate_tasks_context["task_type"] = TaskTypeEnum.generate_course.value

    log.info(
        f"[generate_course] Старт генерации курса для sid={sid}, user_id={user_id}"
    )
    try:
        redis = get_cache_service()
        async with uow_context() as uow:
            await TaskService(uow).create_task(
                TaskIn(
                    id=ctx["job_id"],
                    task_type=generate_tasks_context.get("task_type"),
                    params=generate_tasks_context.get("params"),
                    parent_id=generate_tasks_context.get("parent_task_id"),
                )
            )
            generate_tasks_context["parent_task_id"] = ctx["job_id"]

            await push_and_publish(
                _msg("bot", "Генерируем для вас индивидуальный курс…", "chat_info"), sid
            )
            log.debug(
                f"[generate_course] Вызов create_course_by_user_preference для sid={sid}, user_id={user_id}"
            )
            course = await LearningService(uow).create_course_by_user_preference(
                user_pref, sid=sid, user_id=user_id
            )
            if sid:
                course_data = {
                    "id": str(course.id),
                    "title": course.title,
                    "description": course.description,
                    "estimated_time_hours": course.estimated_time_hours,
                }
                await redis.add_generated_course(sid, course_data)
                log.info(f"[generate_course] Курс добавлен в redis для sid={sid}")

            await push_and_publish(
                _msg("bot", "Структура курса сгенерирована!", "chat_info"), sid
            )
            await push_and_publish(
                _msg(
                    "system",
                    "Структура курса сгенерирована.",
                    "course_created_done",
                ),
                sid,
            )
            log.info(f"[generate_course] Структура курса сгенерирована для sid={sid}")

        if (
            generate_tasks_context["main_task_type"]
            == TaskTypeEnum.generate_course.value
        ):
            if generate_params.get("deep") != GenerateDeepEnum.user_summary.value:
                log.info(
                    f"[generate_course] Запуск генерации плана модулей для course_id={course.id}"
                )
                await ctx["arq_queue"].enqueue_job(
                    "generate_module_plan",
                    course_id=str(course.id),
                    user_pref_summary=user_pref,
                    generate_tasks_context=generate_tasks_context,
                    _queue_name="course_generation",
                )
                log.info(
                    f"[generate_course] Генерация модулей и уроков курса началась для sid={sid}"
                )
        if sid:
            await redis.set_session_status(sid, "course_created")
        return CourseOut.model_validate(course)
    except Exception as e:
        log.exception(
            f"[generate_course] Ошибка при генерации курса для sid={sid}: {e}"
        )
        await push_and_publish(
            _msg("bot", f"Произошла ошибка при создании курса: {str(e)}", "error"),
            sid,
        )
        await push_and_publish(
            _msg("system", "Ошибка при создании курса", "course_creation_error"),
            sid,
        )
        if sid:
            await redis.clear_course_generation_in_progress(sid)
            await redis.set_session_status(sid, "error")
        raise
