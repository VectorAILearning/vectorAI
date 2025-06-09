import asyncio
import enum
import json
import logging
import uuid
from datetime import datetime

from litellm import BaseModel
from models.course import CourseModel, ModuleModel
from models.task import TaskStatusEnum, TaskTypeEnum
from schemas.course import CourseOut, ModuleOut
from schemas.task import TaskIn, TaskOut, TaskPatch
from services import get_cache_service
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from utils import _msg, uow_context
from utils.task_utils import wait_for_task_in_db

log = logging.getLogger(__name__)


class GenerateDeepEnum(enum.Enum):
    user_summary = "user_summary"
    course_base = "course_base"
    course_plan = "course_plan"
    module_plan = "module_plan"
    lesson_content_plan = "lesson_content_plan"
    first_lesson_content = "first_lesson_content"
    content = "content"


class GenerateTaskContext(BaseModel):
    main_task_id: str
    main_task_type: TaskTypeEnum
    deep: str | None = None
    session_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    params: dict | None = None


async def generate_course(
    ctx,
    audit_history: str,
    deep: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> TaskOut:
    """Генерация полного курса
    Args:
        ctx(dict): контекст
        audit_history(str): история аудита
        deep(str): глубина генерации
        session_id(str): id сессии
        user_id(str): id пользователя
    Returns:
        TaskOut: результат генерации задачи
    """
    try:
        redis = get_cache_service()
        generate_tasks_context = GenerateTaskContext(
            main_task_id=ctx["job_id"],
            main_task_type=TaskTypeEnum.generate_course,
            deep=deep,
            session_id=session_id,
            user_id=user_id,
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

            job = await ctx["arq_queue"].enqueue_job(
                "generate_user_summary",
                audit_history=audit_history,
                session_id=session_id,
                user_id=user_id,
                generate_tasks_context=generate_tasks_context,
                _queue_name="course_generation",
            )

            await push_and_publish(
                _msg("bot", "Генерируем для вас индивидуальный курс…", "chat_info"),
                session_id,
            )
            log.info(
                f"[generate_course] Запуск генерации предпочтения пользователя для session_id={session_id}, user_id={user_id}"
            )

            task = await TaskService(uow).create_task(
                TaskIn(
                    id=job.job_id,
                    task_type=TaskTypeEnum.generate_user_summary,
                    params={
                        "deep": deep,
                        "audit_history": audit_history,
                    },
                    session_id=session_id,
                    user_id=user_id,
                    parent_id=ctx["job_id"],
                )
            )
            return task
    except Exception as e:
        log.exception(
            f"[generate_course] Ошибка при запуске генерации полного курса: {e}"
        )
        async with uow_context() as uow:
            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.failed,
                    error_message=str(e),
                    finished_at=datetime.now(),
                ),
            )
        if session_id:
            await redis.clear_course_generation_in_progress(str(session_id))
            await redis.set_session_status(str(session_id), "course_generation_error")
        raise


async def generate_course_base(
    ctx,
    user_pref_id: uuid.UUID,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    generate_tasks_context: GenerateTaskContext | None = None,
) -> CourseOut:
    """
    Базовая генерация курса на основе предпочтений пользователя (название, описание, цель).
    Args:
        ctx: контекст
        user_pref_id: id предпочтения пользователя
        generate_tasks_context: контекст задач генераций
        session_id(uuid.UUID): id сессии
        user_id(uuid.UUID): id пользователя
    Returns:
        CourseOut: курс
    """
    log.info(
        f"[generate_course] Старт генерации курса для session_id={session_id}, user_id={user_id}"
    )
    try:
        redis = get_cache_service()
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
            user_pref = await uow.audit_repo.get_by_id(user_pref_id)
            if not user_pref:
                raise ValueError(f"Preference {user_pref_id} not found")
            course = await LearningService(uow).create_course_by_user_preference(
                user_pref, sid=session_id, user_id=user_id
            )
            if session_id:
                course_data = {
                    "id": str(course.id),
                    "title": course.title,
                    "description": course.description,
                    "estimated_time_hours": course.estimated_time_hours,
                }
                await redis.add_generated_course(str(session_id), course_data)
                log.info(
                    f"[generate_course] Курс добавлен в redis для sid={session_id}"
                )

            await push_and_publish(
                _msg("bot", "Структура курса сгенерирована!", "chat_info"), session_id
            )
            await push_and_publish(
                _msg(
                    "system",
                    "Структура курса сгенерирована.",
                    "course_created_done",
                ),
                session_id,
            )
            log.info(
                f"[generate_course] Структура курса сгенерирована для session_id={session_id}"
            )

            if generate_tasks_context and generate_tasks_context.main_task_type == TaskTypeEnum.generate_course:
                if generate_tasks_context.deep != GenerateDeepEnum.course_base.value:
                    log.info(
                        f"[generate_course] Запуск генерации плана модулей для course_id={course.id}"
                    )
                    job = await ctx["arq_queue"].enqueue_job(
                        "generate_course_plan",
                        course_id=course.id,
                        user_pref_summary=user_pref.summary,
                        session_id=session_id,
                        user_id=user_id,
                        generate_tasks_context=generate_tasks_context,
                        _queue_name="course_generation",
                    )
                    await TaskService(uow).create_task(
                        TaskIn(
                            id=job.job_id,
                            task_type=TaskTypeEnum.generate_course_plan,
                            params={
                                "course_id": str(course.id),
                                "user_pref_summary": user_pref.summary,
                            },
                            session_id=session_id,
                            user_id=user_id,
                            parent_id=ctx["job_id"],
                        )
                    )
                    log.info(
                        f"[generate_course] Генерация модулей и уроков курса началась для session_id={session_id}"
                    )

            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.success,
                    result=json.loads(
                        CourseOut.model_validate(course).model_dump_json()
                    ),
                    finished_at=datetime.now(),
                ),
            )

            if session_id:
                await redis.set_session_status(str(session_id), "course_created_done")

            return CourseOut.model_validate(course)
    except Exception as e:
        log.exception(
            f"[generate_course] Ошибка при генерации курса для session_id={session_id}: {e}"
        )
        async with uow_context() as uow:
            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.failed,
                    error_message=str(e),
                    finished_at=datetime.now(),
                ),
            )
            if generate_tasks_context and generate_tasks_context.main_task_id:
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
                _msg("bot", f"Произошла ошибка при создании курса: {str(e)}", "error"),
                session_id,
            )
            await push_and_publish(
                _msg("system", "Ошибка при создании курса", "course_generation_error"),
                session_id,
            )
            await redis.clear_course_generation_in_progress(str(session_id))
            await redis.set_session_status(str(session_id), "course_generation_error")
        raise


async def generate_course_plan(
    ctx,
    course_id: uuid.UUID,
    user_pref_summary: str,
    generate_tasks_context: GenerateTaskContext | None = None,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> list[ModuleOut]:
    """
    Базовая генерация курса (модулей в курсе). Название, описание, цель модулей.
    Args:
        ctx: контекст
        course_id (uuid.UUID): id курса
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
        session_id(uuid.UUID): id сессии
        user_id(uuid.UUID): id пользователя
    Returns:
        list[ModuleOut]: список модулей
    """
    log.info(
        f"[generate_course_plan] Старт генерации плана модулей для course_id={course_id}, session_id={session_id}, user_id={user_id}"
    )
    try:
        redis = get_cache_service()
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
            course = await LearningService(uow).get_course_by_id(course_id)
            if not course:
                log.error(f"[generate_course_plan] Курс {course_id} не найден")
                raise ValueError(f"Курс {course_id} не найден")

            modules = await LearningService(uow).create_modules_plan_by_course_id(
                course_id, user_pref_summary
            )

        if generate_tasks_context and generate_tasks_context.main_task_type == TaskTypeEnum.generate_course:
            if generate_tasks_context.deep != GenerateDeepEnum.course_plan.value:
                first_module = min(modules, key=lambda m: m.position)
                job = await ctx["arq_queue"].enqueue_job(
                    "generate_module_plan",
                    first_module.id,
                    user_pref_summary,
                    session_id,
                    user_id,
                    generate_tasks_context,
                    _queue_name="course_generation",
                )
                await TaskService(uow).create_task(
                    TaskIn(
                        id=job.job_id,
                        task_type=TaskTypeEnum.generate_module_plan,
                        params={
                            "module_id": str(first_module.id),
                            "user_pref_summary": user_pref_summary,
                        },
                        session_id=session_id,
                        user_id=user_id,
                        parent_id=ctx["job_id"],
                    )
                )

        await TaskService(uow).partial_update_task(
            ctx["job_id"],
            TaskPatch(
                status=TaskStatusEnum.success,
                result=[
                    json.loads(ModuleOut.model_validate(module).model_dump_json())
                    for module in modules
                ],
                finished_at=datetime.now(),
            ),
        )
        return [ModuleOut.model_validate(module) for module in modules]
    except Exception as e:
        log.exception(
            f"[generate_module_plan] Ошибка при генерации плана модулей для session_id={session_id}: {e}"
        )
        async with uow_context() as uow:
            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.failed,
                    error_message=str(e),
                    finished_at=datetime.now(),
                ),
            )
            if generate_tasks_context and generate_tasks_context.main_task_id:
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
                    f"Произошла ошибка при создании плана модулей: {str(e)}",
                    "error",
                ),
                session_id,
            )
            await push_and_publish(
                _msg(
                    "system",
                    "Ошибка при создании плана модулей",
                    "module_plan_creation_error",
                ),
                session_id,
            )
            await redis.clear_course_generation_in_progress(str(session_id))
            await redis.set_session_status(str(session_id), "course_generation_error")
        raise
