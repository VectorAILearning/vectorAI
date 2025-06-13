import logging
import uuid

from models.task import TaskTypeEnum
from schemas.audit import PreferenceOut
from schemas.generate import GenerateDeepEnum, GenerateTaskContext
from services.message_bus import push_and_publish
from utils import _msg, uow_context
from workers.generate_tasks.helpers import (
    _fail_course_generation_session,
    _fail_task,
    _finish_course_generation_session,
    _finish_task,
    _spawn_course_base_task,
    _start_task,
)

log = logging.getLogger(__name__)


async def generate_user_summary(
    ctx,
    audit_history: str,
    generate_tasks_context: GenerateTaskContext,
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
        PreferenceOut: предпочтение пользователя
    """
    from services.audit_service.service import AuditDialogService

    try:
        await push_and_publish(
            _msg("bot", "Анализируем ваши предпочтения…", "chat_info"), session_id
        )
        async with uow_context() as uow:
            await _start_task(uow, ctx["job_id"])

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
                    await _spawn_course_base_task(
                        ctx,
                        user_pref.id,
                        generate_tasks_context,
                        session_id,
                        user_id,
                        ctx["job_id"],
                    )
                else:
                    await _finish_course_generation_session(session_id)

            await _finish_task(
                uow,
                ctx["job_id"],
                PreferenceOut.model_validate(user_pref).model_dump_json(),
            )

            return PreferenceOut.model_validate(user_pref)
    except Exception as e:
        log.exception(
            f"Ошибка при генерации предпочтения пользователя: {e} session_id={session_id}"
        )
        await _fail_course_generation_session(session_id)
        async with uow_context() as uow:
            await _fail_task(ctx["job_id"], str(e))

            if generate_tasks_context.main_task_id:
                await _fail_task(generate_tasks_context.main_task_id, str(e))
        raise
