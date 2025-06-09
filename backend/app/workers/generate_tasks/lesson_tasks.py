import json
import logging
import uuid
from datetime import datetime

from models.content import ContentModel
from models.course import LessonModel, ModuleModel
from models.task import TaskStatusEnum, TaskTypeEnum
from schemas.course import ContentOut
from schemas.task import TaskIn, TaskPatch
from services import get_cache_service
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils import _msg, uow_context
from utils.task_utils import wait_for_task_in_db
from workers.generate_tasks.course_tasks import GenerateDeepEnum, GenerateTaskContext

log = logging.getLogger(__name__)


async def generate_lesson_content_plan(
    ctx,
    lesson_id: uuid.UUID,
    user_pref_summary: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    generate_tasks_context: GenerateTaskContext | None = None,
) -> list[dict]:
    """
    Базовая генерация контент-плана урока (блоков контента в уроке). Название, описание, цель блоков контента.
    Args:
        ctx: контекст
        lesson_id: id урока
        session_id (uuid.UUID): id сессии
        user_id (uuid.UUID): id пользователя
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        list[ContentOut]: список блоков контента
    """
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

            lesson = await LearningService(uow).get_lesson_by_id(lesson_id)
            if not lesson:
                log.error(f"[generate_lesson_plan] Урок {lesson_id} не найден")
                raise ValueError(f"Урок {lesson_id} не найден")

            log.info(
                f"[generate_lesson_plan] Генерация контент-плана для урока {lesson_id}"
            )
            content_list = await LearningService(
                uow
            ).generate_and_save_lesson_content_plan(lesson_id, user_pref_summary)
            log.info(
                f"[generate_lesson_plan] Контент-план для урока {lesson_id} сгенерирован"
            )

        if (
            generate_tasks_context
            and generate_tasks_context.main_task_type == TaskTypeEnum.generate_course
        ):
            if (
                generate_tasks_context.deep
                != GenerateDeepEnum.lesson_content_plan.value
            ):
                if (
                    generate_tasks_context.deep
                    == GenerateDeepEnum.first_lesson_content.value
                ):
                    first_content_block = min(content_list, key=lambda c: c.position)
                    job = await ctx["arq_queue"].enqueue_job(
                        "generate_content",
                        first_content_block.id,
                        lesson_id,
                        user_pref_summary,
                        session_id,
                        user_id,
                        generate_tasks_context,
                        _queue_name="course_generation",
                    )
                    await TaskService(uow).create_task(
                        TaskIn(
                            id=job.job_id,
                            task_type=TaskTypeEnum.generate_content,
                            params={
                                "content_block_id": str(first_content_block.id),
                                "lesson_id": str(lesson.id),
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
                            result=json.loads(
                                ContentOut.model_validate(
                                    first_content_block
                                ).model_dump_json()
                            ),
                            finished_at=datetime.now(),
                        ),
                    )
                    return [
                        ContentOut.model_validate(content).model_dump()
                        for content in content_list
                    ]

                next_lesson = await uow.session.execute(
                    select(LessonModel)
                    .where(LessonModel.module_id == lesson.module_id)
                    .where(LessonModel.position == lesson.position + 1)
                )
                next_lesson = next_lesson.scalar_one_or_none()
                if next_lesson:
                    log.info(
                        f"[generate_lesson_plan] Следующий урок найден: id={next_lesson.id}, position={next_lesson.position}"
                    )
                    job = await ctx["arq_queue"].enqueue_job(
                        "generate_lesson_content_plan",
                        next_lesson.id,
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
                                "lesson_id": str(next_lesson.id),
                                "user_pref_summary": user_pref_summary,
                            },
                            session_id=session_id,
                            user_id=user_id,
                            parent_id=ctx["job_id"],
                        )
                    )
                else:
                    next_module = await uow.session.execute(
                        select(ModuleModel)
                        .where(ModuleModel.course_id == lesson.module.course_id)
                        .where(ModuleModel.position == lesson.module.position + 1)
                    )
                    next_module = next_module.scalar_one_or_none()
                    if next_module:
                        log.info(
                            f"[generate_lesson_plan] Следующий модуль найден: id={next_module.id}, position={next_module.position}"
                        )
                        next_module_first_lesson = min(
                            next_module.lessons, key=lambda l: l.position
                        )
                        job = await ctx["arq_queue"].enqueue_job(
                            "generate_lesson_content_plan",
                            next_module_first_lesson.id,
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
                                    "lesson_id": str(next_module_first_lesson.id),
                                    "user_pref_summary": user_pref_summary,
                                },
                                session_id=session_id,
                                user_id=user_id,
                                parent_id=ctx["job_id"],
                            )
                        )
                    else:
                        first_module = (
                            await uow.session.execute(
                                select(ModuleModel)
                                .options(
                                    selectinload(ModuleModel.lessons).selectinload(
                                        LessonModel.contents
                                    )
                                )
                                .where(ModuleModel.course_id == lesson.module.course_id)
                                .where(ModuleModel.position == 1)
                                .limit(1)
                            )
                        ).scalar_one_or_none()
                        if not first_module:
                            raise ValueError(f"Модуль не найден для урока {lesson_id}")

                        first_lesson = min(
                            first_module.lessons, key=lambda l: l.position
                        )
                        if not first_lesson:
                            raise ValueError(
                                f"Урок не найден для модуля {first_module.id}"
                            )

                        first_content_block = min(
                            first_lesson.contents, key=lambda c: c.position
                        )
                        if not first_content_block:
                            raise ValueError(
                                f"Блок контента не найден для урока {first_lesson.id}"
                            )

                        job = await ctx["arq_queue"].enqueue_job(
                            "generate_content",
                            first_content_block.id,
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
                                task_type=TaskTypeEnum.generate_content,
                                params={
                                    "content_block_id": str(first_content_block.id),
                                    "lesson_id": str(first_lesson.id),
                                    "user_pref_summary": user_pref_summary,
                                },
                                session_id=session_id,
                                user_id=user_id,
                                parent_id=ctx["job_id"],
                            )
                        )
                        log.info(
                            f"[generate_lesson_plan] Нет следующего модуля после урока {lesson_id}, завершаем генерацию курса"
                        )
                        if session_id:
                            await redis.clear_course_generation_in_progress(
                                str(session_id)
                            )
        await TaskService(uow).partial_update_task(
            ctx["job_id"],
            TaskPatch(
                status=TaskStatusEnum.success,
                result=[
                    json.loads(ContentOut.model_validate(content).model_dump_json())
                    for content in content_list
                ],
                finished_at=datetime.now(),
            ),
        )
        return [
            ContentOut.model_validate(content).model_dump() for content in content_list
        ]
    except Exception as e:
        log.exception(
            f"[generate_lesson_plan] Ошибка при генерации урока для session_id={session_id}, user_id={user_id}: {e}"
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
                _msg("bot", f"Произошла ошибка при создании урока: {str(e)}", "error"),
                str(session_id),
            )
            await push_and_publish(
                _msg("system", "Ошибка при создании урока", "lesson_creation_error"),
                str(session_id),
            )
            await redis.clear_course_generation_in_progress(str(session_id))
            await redis.set_session_status(str(session_id), "course_generation_error")
        raise
