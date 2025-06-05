import logging

from models import ContentModel, CourseModel, LessonModel, ModuleModel
from models.task import TaskTypeEnum
from schemas.task import TaskIn
from services.content_service.service import ContentService
from services.task_service.service import TaskService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils.uow import uow_context
from workers.generate_tasks.generate_tasks import GenerateDeepEnum
from services import get_cache_service

log = logging.getLogger(__name__)


async def generate_block_content(
    ctx,
    content_block_id: str,
    lesson_id: str,
    user_pref_summary: str,
    generate_tasks_context: dict,
):
    """
    Генерация контента для блока, запуск генерации блоков контента следующих уроков.
    Args:
        ctx: контекст
        content_block_id: id блока контента
        lesson_id: id урока
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    """
    sid = generate_tasks_context["params"].get("sid")
    user_id = generate_tasks_context["params"].get("user_id")
    generate_params = generate_tasks_context["params"]

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
            lesson = content_block.lesson if content_block else None
            if not content_block or not lesson:
                log.error(
                    f"Block or lesson not found: content_block_id={content_block_id}, lesson_id={lesson_id}"
                )
                return
            log.debug(
                f"Начинаю генерацию контента для блока: content_block_id={content_block_id}, type={content_block.type}, description={content_block.description}, goal={content_block.goal}"
            )
            try:
                await ContentService(uow).generate_content_by_block(content_block)
                log.debug(
                    f"Контент успешно сгенерирован и сохранён для блока: content_block_id={content_block_id}"
                )
            except Exception as e:
                log.exception(
                    f"Ошибка при генерации контента для блока: content_block_id={content_block_id}, error={e}"
                )
                if sid:
                    await redis.clear_course_generation_in_progress(sid)
                return

            if generate_tasks_context["task_type"] == TaskTypeEnum.generate_course.value:
                if generate_params.get("deep") != GenerateDeepEnum.lesson.value:
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
                        await ctx["arq_queue"].enqueue_job(
                            "generate_block_content",
                            content_block_id=str(next_content_block.id),
                            lesson_id=lesson_id,
                            user_pref_summary=user_pref_summary,
                            generate_tasks_context=generate_tasks_context,
                            _queue_name="course_generation",
                        )
                        log.info(
                            f"Задача на генерацию контента для блока {next_content_block.id} поставлена в очередь"
                        )
                    else:
                        if generate_params.get("deep") != GenerateDeepEnum.first_lesson.value:
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
                                await ctx["arq_queue"].enqueue_job(
                                    "generate_block_content",
                                    content_block_id=str(first_content_block.id),
                                    lesson_id=str(next_lesson.id),
                                    user_pref_summary=user_pref_summary,
                                    generate_tasks_context=generate_tasks_context,
                                    _queue_name="course_generation",
                                )
                                log.info(
                                    f"Задача на генерацию контента для блока {first_content_block.id} поставлена в очередь"
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
                                    await ctx["arq_queue"].enqueue_job(
                                        "generate_block_content",
                                        content_block_id=str(first_content_block.id),
                                        lesson_id=str(next_module_first_lesson.id),
                                        user_pref_summary=user_pref_summary,
                                        generate_tasks_context=generate_tasks_context,
                                        _queue_name="course_generation",
                                    )
                                    log.info(
                                        f"Задача на генерацию контента для блока {first_content_block.id} поставлена в очередь"
                                    )
                                else:
                                    log.info(
                                        f"Нет следующего модуля после урока {lesson_id} и блока {content_block_id}, завершаем генерацию курса"
                                    )
                                    if sid:
                                        await redis.clear_course_generation_in_progress(sid)
                        else:
                            if sid:
                                await redis.clear_course_generation_in_progress(sid)
                                
    except Exception as e:
        log.exception(f"[generate_block_content] Ошибка при генерации блока для sid={sid}: {e}")
        if sid:
            await redis.clear_course_generation_in_progress(sid)
        raise
