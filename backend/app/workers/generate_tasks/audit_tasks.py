import logging
import time
import uuid

from models.base import PreferenceModel
from models.task import TaskTypeEnum
from schemas.task import TaskIn
from services import get_cache_service
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from utils.uow import uow_context
from workers.generate_tasks.generate_tasks import GenerateDeepEnum

log = logging.getLogger(__name__)


def _msg(who: str, text: str, type_: str = "chat") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "ts": time.time(),
        "who": who,
        "text": text,
        "type": type_,
    }


async def generate_user_summary(
    ctx, audit_history: str, generate_tasks_context: dict
) -> PreferenceModel:
    """
    Генерация предпочтения пользователя по курсу на основе истории аудита.
    Args:
        ctx: контекст
        history: история аудита
        generate_tasks_context: контекст задач генераций
    Returns:
        PreferenceModel: предпочтение пользователя
    """
    from services.audit_service.service import AuditDialogService

    sid = generate_tasks_context["params"].get("sid")
    user_id = generate_tasks_context["params"].get("user_id")
    generate_tasks_context["task_type"] = TaskTypeEnum.generate_user_summary.value
    try:
        redis = get_cache_service()
        await push_and_publish(_msg("bot", "Анализируем ваши предпочтения…"), sid)
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
            user_pref = await AuditDialogService(
                uow
            ).create_user_preference_by_audit_history(
                audit_history, sid=sid, user_id=user_id
            )

        await push_and_publish(
            _msg(
                "system",
                f"Предпочтение пользователя: {user_pref.summary}",
                "system",
            ),
            sid,
        )
        await push_and_publish(
            _msg("bot", "Предпочтение пользователя сгенерировано"), sid
        )

        if (
            generate_tasks_context["main_task_type"]
            == TaskTypeEnum.generate_course.value
        ):
            if (
                generate_tasks_context["params"].get("deep")
                != GenerateDeepEnum.user_summary.value
            ):
                await ctx["arq_queue"].enqueue_job(
                    "generate_course_by_user_preference",
                    generate_tasks_context=generate_tasks_context,
                    user_pref=user_pref,
                    _queue_name="course_generation",
                )

        return user_pref
    except Exception as e:
        log.exception(f"Ошибка при генерации предпочтения пользователя: {e}")
        await push_and_publish(
            _msg(
                "bot",
                f"Произошла ошибка при генерации предпочтения пользователя: {e}",
                "error",
            ),
            sid,
        )
        await push_and_publish(
            _msg(
                "system",
                "Ошибка при генерации предпочтения пользователя",
                "user_preference_generation_error",
            ),
            sid,
        )
        if sid:
            await redis.clear_course_generation_in_progress(sid)
            await redis.set_session_status(sid, "error")
        raise
