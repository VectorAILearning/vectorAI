import json
import logging
import uuid
from datetime import datetime

from models.base import PreferenceModel
from models.task import TaskStatusEnum, TaskTypeEnum
from schemas.audit import PreferenceOut
from schemas.task import TaskIn, TaskOut, TaskPatch
from services import get_cache_service
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from utils import _msg, uow_context
from utils.task_utils import wait_for_task_in_db
from workers.generate_tasks.course_tasks import GenerateDeepEnum, GenerateTaskContext

log = logging.getLogger(__name__)


async def generate_user_summary(
    ctx,
    audit_history: str,
    generate_tasks_context: GenerateTaskContext | None = None,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> PreferenceOut:
    """
    Генерация предпочтения пользователя по курсу на основе истории аудита.
    Args:
        ctx: контекст
        audit_history(str): история аудита
        generate_tasks_context(GenerateTaskContext): контекст задач генераций
        session_id(uuid.UUID): id сессии
        user_id(uuid.UUID): id пользователя
    Returns:
        PreferenceModel: предпочтение пользователя
    """
    from services.audit_service.service import AuditDialogService

    try:
        redis = get_cache_service()
        await push_and_publish(
            _msg("bot", "Анализируем ваши предпочтения…", "chat_info"), session_id
        )
        async with uow_context() as uow:
            task = await wait_for_task_in_db(uow.task_repo, ctx["job_id"])
            if not task:
                raise Exception(f"Task {ctx['job_id']} not found in DB")
            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.in_progress,
                    started_at=datetime.now(),
                ),
            )

            user_pref = (
                await AuditDialogService().create_user_preference_by_audit_history(
                    audit_history=audit_history,
                    sid=session_id,
                    user_id=user_id,
                )
            )

            await push_and_publish(
                _msg(
                    "system",
                    f"Предпочтение пользователя: {user_pref.summary}",
                    "system",
                ),
                session_id,
            )
            await push_and_publish(
                _msg("bot", "Предпочтение пользователя сгенерировано", "chat_info"),
                session_id,
            )
            if generate_tasks_context.main_task_type == TaskTypeEnum.generate_course:
                if generate_tasks_context.deep != GenerateDeepEnum.user_summary.value:
                    job = await ctx["arq_queue"].enqueue_job(
                        "generate_course_base",
                        generate_tasks_context=generate_tasks_context,
                        user_pref_id=user_pref.id,
                        session_id=session_id,
                        user_id=user_id,
                        _queue_name="course_generation",
                    )
                    task = await TaskService(uow).create_task(
                        TaskIn(
                            id=job.job_id,
                            task_type=TaskTypeEnum.generate_course_base,
                            params={"user_pref_id": str(user_pref.id)},
                            session_id=session_id,
                            user_id=user_id,
                            parent_id=ctx["job_id"],
                        )
                    )

            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.success,
                    result=json.loads(
                        PreferenceOut.model_validate(user_pref).model_dump_json()
                    ),
                    finished_at=datetime.now(),
                ),
            )
            return PreferenceOut.model_validate(user_pref)
    except Exception as e:
        log.exception(
            f"Ошибка при генерации предпочтения пользователя: {e} session_id={session_id}"
        )

        async with uow_context() as uow:
            task = await wait_for_task_in_db(uow.task_repo, ctx["job_id"])
            if not task:
                raise Exception(f"Task {ctx['job_id']} not found in DB")
            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.failed,
                    error_message=str(e),
                    finished_at=datetime.now(),
                ),
            )
            if generate_tasks_context and generate_tasks_context.main_task_id:
                parent_task = await wait_for_task_in_db(
                    uow.task_repo, generate_tasks_context.main_task_id
                )
                if not parent_task:
                    raise Exception(
                        f"Task {generate_tasks_context.main_task_id} not found in DB"
                    )
                await TaskService(uow).partial_update_task(
                    generate_tasks_context.main_task_id,
                    TaskPatch(
                        status=TaskStatusEnum.failed,
                        error_message=str(e),
                        finished_at=datetime.now(),
                    ),
                )

        if session_id:
            await push_and_publish(
                _msg(
                    "bot",
                    f"Произошла ошибка при генерации предпочтения пользователя: {e}",
                    "course_generation_error",
                ),
                session_id,
            )
            await push_and_publish(
                _msg(
                    "system",
                    "Ошибка при генерации предпочтения пользователя",
                    "course_generation_error",
                ),
                session_id,
            )
            await redis.clear_course_generation_in_progress(session_id)
            await redis.set_session_status(session_id, "course_generation_error")

        raise
