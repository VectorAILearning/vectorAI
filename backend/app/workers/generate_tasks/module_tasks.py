import json
import logging
import uuid
from datetime import datetime

from models.course import ModuleModel
from models.task import TaskStatusEnum, TaskTypeEnum
from schemas import LessonOut
from schemas.task import TaskIn, TaskPatch
from services import get_cache_service
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from sqlalchemy import select
from utils import _msg, uow_context
from utils.task_utils import wait_for_task_in_db
from workers.generate_tasks.course_tasks import GenerateDeepEnum, GenerateTaskContext

log = logging.getLogger(__name__)


async def generate_module_plan(
    ctx,
    module_id: uuid.UUID,
    user_pref_summary: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    generate_tasks_context: GenerateTaskContext | None = None,
) -> list[LessonOut]:
    """
    Базовая генерация модуля курса (уроков в модуле). Название, описание, цель уроков.
    Args:
        ctx: контекст
        module_id (uuid.UUID): id модуля
        user_pref_summary: предпочтения пользователя
        session_id (uuid.UUID): id сессии
        user_id (uuid.UUID): id пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        ModuleModel: модуль
    """
    log.info(
        f"[generate_module] Генерация модуля {module_id} для session_id={session_id}, user_id={user_id}"
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

            module = await LearningService(uow).get_module_by_id(module_id)
            if not module:
                log.error(f"[generate_module] Модуль {module_id} не найден")
                raise ValueError(f"Модуль {module_id} не найден")

            lessons = await LearningService(uow).create_lessons_plan_by_module_id(
                module_id, user_pref_summary
            )
            log.info(
                f"[generate_module] План уроков для модуля {module.title} сгенерирован"
            )

            if generate_tasks_context.main_task_type == TaskTypeEnum.generate_course:
                if generate_tasks_context.deep != GenerateDeepEnum.module_plan.value:
                    next_module = await uow.session.execute(
                        select(ModuleModel)
                        .where(ModuleModel.course_id == module.course_id)
                        .where(ModuleModel.position == module.position + 1)
                    )
                    next_module = next_module.scalar_one_or_none()
                    if next_module:
                        log.info(
                            f"[generate_module] Следующий модуль найден: id={next_module.id}, position={next_module.position}"
                        )
                        job = await ctx["arq_queue"].enqueue_job(
                            "generate_module_plan",
                            next_module.id,
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
                                    "module_id": str(next_module.id),
                                    "user_pref_summary": user_pref_summary,
                                },
                                session_id=session_id,
                                user_id=user_id,
                                parent_id=ctx["job_id"],
                            )
                        )
                    else:
                        log.info(
                            f"[generate_module] Нет следующего модуля после модуля {module.title}"
                        )
                        log.info(f"[generate_module] Начинаем генерацию контент-плана")
                        first_module = await uow.session.execute(
                            select(ModuleModel)
                            .where(ModuleModel.course_id == module.course_id)
                            .where(ModuleModel.position == 1)
                            .limit(1)
                        )
                        first_module = first_module.scalar_one_or_none()
                        first_lesson = min(
                            first_module.lessons, key=lambda l: l.position
                        )
                        job = await ctx["arq_queue"].enqueue_job(
                            "generate_lesson_content_plan",
                            first_lesson.id,
                            user_pref_summary,
                            session_id,
                            user_id,
                            generate_tasks_context,
                            _queue_name="course_generation",
                        )
                        await TaskService(uow).create_task(
                            TaskIn(
                                id=job.job_id,
                                task_type=TaskTypeEnum.generate_lesson_content_plan,
                                params={
                                    "lesson_id": str(first_lesson.id),
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
                        json.loads(LessonOut.model_validate(lesson).model_dump_json())
                        for lesson in lessons
                    ],
                    finished_at=datetime.now(),
                ),
            )
            return [LessonOut.model_validate(lesson).model_dump() for lesson in lessons]
    except Exception as e:
        log.exception(
            f"[generate_module] Ошибка при генерации модуля для session_id={session_id}, user_id={user_id}: {e}"
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
                _msg("bot", f"Произошла ошибка при создании модуля: {str(e)}", "error"),
                session_id,
            )
            await push_and_publish(
                _msg("system", "Ошибка при создании модуля", "module_creation_error"),
                session_id,
            )
            await redis.clear_course_generation_in_progress(session_id)
        raise
