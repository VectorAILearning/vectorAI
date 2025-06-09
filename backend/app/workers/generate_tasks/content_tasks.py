import json
import logging
import uuid
from datetime import datetime

from models import ContentModel, CourseModel, LessonModel, ModuleModel
from models.task import TaskStatusEnum, TaskTypeEnum
from schemas.course import ContentOut
from schemas.task import TaskIn, TaskPatch
from services import get_cache_service
from services.content_service.service import ContentService
from services.task_service.service import TaskService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils import uow_context
from utils.task_utils import wait_for_task_in_db
from workers.generate_tasks.course_tasks import GenerateDeepEnum, GenerateTaskContext

log = logging.getLogger(__name__)


async def generate_content(
    ctx,
    content_block_id: uuid.UUID,
    lesson_id: uuid.UUID,
    user_pref_summary: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    generate_tasks_context: GenerateTaskContext | None = None,
) -> ContentOut:
    """
    Генерация контента для блока контента в уроке. Сам контент.
    Args:
        ctx: контекст
        content_block_id: id блока контента
        lesson_id: id урока
        session_id: id сессии
        user_id: id пользователя
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        ContentOut: блок контента
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
            content_block = await uow.session.get(
                ContentModel,
                content_block_id,
                options=[
                    selectinload(ContentModel.lesson)
                    .selectinload(LessonModel.module)
                    .selectinload(ModuleModel.course)
                    .selectinload(CourseModel.modules)
                    .selectinload(ModuleModel.lessons)
                    .selectinload(LessonModel.contents)
                ],
            )
            if not content_block:
                log.error(f"Блок контента {content_block_id} не найден")
                raise ValueError(f"Блок контента {content_block_id} не найден")

            lesson = content_block.lesson
            if not lesson:
                log.error(
                    f"Block or lesson not found: content_block_id={content_block_id}, lesson_id={lesson_id}"
                )
                raise ValueError(f"Урок {lesson_id} не найден")

            log.debug(
                f"Начинаю генерацию контента для блока: content_block_id={content_block_id}, type={content_block.type}, description={content_block.description}, goal={content_block.goal}"
            )
            await ContentService(uow).generate_content_by_block(content_block)
            log.debug(
                f"Контент успешно сгенерирован и сохранён для блока: content_block_id={content_block_id}"
            )

            if generate_tasks_context and generate_tasks_context.main_task_type == TaskTypeEnum.generate_course:
                if (generate_tasks_context.deep != GenerateDeepEnum.lesson_content_plan.value):
                    next_content_block = await uow.session.execute(
                        select(ContentModel)
                        .where(ContentModel.lesson_id == lesson_id)
                        .where(ContentModel.position == content_block.position + 1)
                    )
                    next_content_block = next_content_block.scalar_one_or_none()
                    if next_content_block:
                        log.info(
                            f"Следующий блок найден: id={next_content_block.id}, type={next_content_block.type}, position={next_content_block.position}"
                        )
                        job = await ctx["arq_queue"].enqueue_job(
                            "generate_content",
                            next_content_block.id,
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
                                    "content_block_id": str(next_content_block.id),
                                    "lesson_id": str(lesson_id),
                                    "user_pref_summary": user_pref_summary,
                                },
                                session_id=session_id,
                                user_id=user_id,
                                parent_id=ctx["job_id"],
                            )
                        )
                        log.info(
                            f"Задача на генерацию контента для блока {next_content_block.id} поставлена в очередь"
                        )
                    else:
                        if (generate_tasks_context.deep == GenerateDeepEnum.first_lesson_content.value):
                            if (generate_tasks_context.main_task_id):
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
                                        status=TaskStatusEnum.success,
                                        result="course_generation_done",
                                        finished_at=datetime.now(),
                                    ),
                                )
                                if session_id:
                                    await redis.clear_course_generation_in_progress(str(session_id))
                                    await redis.set_session_status(str(session_id), "course_generation_done")
                        else:
                            next_lesson = await uow.session.execute(
                                select(LessonModel)
                                .where(LessonModel.module_id == lesson.module_id)
                                .where(LessonModel.position == lesson.position + 1)
                            )
                            next_lesson = next_lesson.scalar_one_or_none()
                            if next_lesson:
                                log.info(
                                    f"Следующий урок найден: id={next_lesson.id}, position={next_lesson.position}"
                                )
                                first_content_block = min(
                                    next_lesson.contents, key=lambda b: b.position
                                )
                                job = await ctx["arq_queue"].enqueue_job(
                                    "generate_content",
                                    first_content_block.id,
                                    next_lesson.id,
                                    user_pref_summary,
                                    session_id=session_id,
                                    user_id=user_id,
                                    generate_tasks_context=generate_tasks_context,
                                    _queue_name="course_generation",
                                )
                                log.info(
                                    f"Задача на генерацию контента для блока {first_content_block.id} поставлена в очередь"
                                )
                                await TaskService(uow).create_task(
                                    TaskIn(
                                        id=job.job_id,
                                        task_type=TaskTypeEnum.generate_content,
                                        params={
                                            "content_block_id": str(
                                                first_content_block.id
                                            ),
                                            "lesson_id": str(next_lesson.id),
                                            "user_pref_summary": user_pref_summary,
                                        },
                                        session_id=session_id,
                                        user_id=user_id,
                                        parent_id=ctx["job_id"],
                                    )
                                )
                            else:
                                module = lesson.module
                                next_module = await uow.session.execute(
                                    select(ModuleModel)
                                    .where(ModuleModel.course_id == module.course_id)
                                    .where(ModuleModel.position == module.position + 1)
                                )
                                next_module = next_module.scalar_one_or_none()
                                if next_module:
                                    log.info(
                                        f"Следующий модуль найден: id={next_module.id}, position={next_module.position}"
                                    )
                                    next_module_first_lesson = min(
                                        next_module.lessons, key=lambda l: l.position
                                    )
                                    first_content_block = min(
                                        next_module_first_lesson.contents,
                                        key=lambda b: b.position,
                                    )
                                    job = await ctx["arq_queue"].enqueue_job(
                                        "generate_content",
                                        first_content_block.id,
                                        next_module_first_lesson.id,
                                        user_pref_summary,
                                        session_id=session_id,
                                        user_id=user_id,
                                        generate_tasks_context=generate_tasks_context,
                                        _queue_name="course_generation",
                                    )
                                    await TaskService(uow).create_task(
                                        TaskIn(
                                            id=job.job_id,
                                            task_type=TaskTypeEnum.generate_content,
                                            params={
                                                "content_block_id": str(
                                                    first_content_block.id
                                                ),
                                                "lesson_id": str(
                                                    next_module_first_lesson.id
                                                ),
                                                "user_pref_summary": user_pref_summary,
                                            },
                                            session_id=session_id,
                                            user_id=user_id,
                                            parent_id=ctx["job_id"],
                                        )
                                    )
                                    log.info(
                                        f"Задача на генерацию контента для блока {first_content_block.id} поставлена в очередь"
                                    )
                                else:
                                    log.info(
                                        f"Нет следующего модуля после урока {lesson_id} и блока {content_block_id}, завершаем генерацию курса"
                                    )
                                    if (generate_tasks_context.main_task_id):
                                        parent_task = await wait_for_task_in_db(
                                            uow.task_repo,
                                            generate_tasks_context.main_task_id,
                                        )
                                        if not parent_task:
                                            raise Exception(
                                                f"Task {generate_tasks_context.main_task_id} not found in DB"
                                            )
                                        await TaskService(uow).partial_update_task(
                                            generate_tasks_context.main_task_id,
                                            TaskPatch(
                                                status=TaskStatusEnum.success,
                                                result="course_generation_done",
                                                finished_at=datetime.now(),
                                            ),
                                        )
                                        if session_id:
                                            await redis.clear_course_generation_in_progress(str(session_id))
                                            await redis.set_session_status(str(session_id), "course_generation_done")

            await TaskService(uow).partial_update_task(
                ctx["job_id"],
                TaskPatch(
                    status=TaskStatusEnum.success,
                    result=json.loads(
                        ContentOut.model_validate(content_block).model_dump_json()
                    ),
                    finished_at=datetime.now(),
                ),
            )
            return ContentOut.model_validate(content_block)

    except Exception as e:
        log.exception(
            f"[generate_block_content] Ошибка при генерации блока для session_id={session_id}, user_id={user_id}: {e}"
        )
        async with uow_context() as uow:
            if session_id:
                await redis.clear_course_generation_in_progress(str(session_id))
                await redis.set_session_status(str(session_id), "course_generation_error")

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
        raise
