import logging

from models.content import ContentModel
from models.course import LessonModel, ModuleModel
from models.task import TaskTypeEnum
from schemas.task import TaskIn
from services import get_cache_service
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils.uow import uow_context
from workers.generate_tasks.audit_tasks import _msg
from workers.generate_tasks.generate_tasks import GenerateDeepEnum

log = logging.getLogger(__name__)


async def generate_lesson_plan(
    ctx, lesson_id: str, user_pref_summary: str, generate_tasks_context: dict
) -> list[ContentModel]:
    """
    Генерация контент-плана урока на основе предпочтений пользователя.
    Args:
        ctx: контекст
        lesson_id: id урока
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        list[ContentModel]: список блоков контента
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
            lesson = await LearningService(uow).get_lesson_by_id(lesson_id)
            if not lesson:
                log.error(f"[generate_lesson_plan] Урок {lesson_id} не найден")
                return

            log.info(
                f"[generate_lesson_plan] Генерация контент-плана для урока {lesson_id}"
            )
            await push_and_publish(
                _msg("bot", f"Генерируем контент-план для урока {lesson.title}…"), sid
            )
            content_list = await LearningService(
                uow
            ).generate_and_save_lesson_content_plan(lesson_id, user_pref_summary)
            log.info(
                f"[generate_lesson_plan] Контент-план для урока {lesson_id} сгенерирован"
            )

            await push_and_publish(
                _msg("bot", f"Контент-план урока {lesson.title} сгенерирован!"), sid
            )

        if generate_tasks_context["task_type"] == TaskTypeEnum.generate_course.value:
            if generate_params.get("deep") != GenerateDeepEnum.lesson.value:
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
                    await ctx["arq_queue"].enqueue_job(
                        "generate_lesson_plan",
                        lesson_id=str(next_lesson.id),
                        user_pref_summary=user_pref_summary,
                        generate_tasks_context=generate_tasks_context,
                        _queue_name="course_generation",
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
                        await ctx["arq_queue"].enqueue_job(
                            "generate_lesson_plan",
                            lesson_id=str(next_module_first_lesson.id),
                            user_pref_summary=user_pref_summary,
                            generate_tasks_context=generate_tasks_context,
                            _queue_name="course_generation",
                        )
                    else:
                        first_module = await uow.session.execute(
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
                        first_module = first_module.scalar_one_or_none()
                        first_lesson = min(
                            first_module.lessons, key=lambda l: l.position
                        )
                        first_content_block = min(
                            first_lesson.contents, key=lambda c: c.position
                        )
                        await ctx["arq_queue"].enqueue_job(
                            "generate_block_content",
                            content_block_id=str(first_content_block.id),
                            lesson_id=str(first_lesson.id),
                            user_pref_summary=user_pref_summary,
                            generate_tasks_context=generate_tasks_context,
                            _queue_name="course_generation",
                        )
                        log.info(
                            f"[generate_lesson_plan] Нет следующего модуля после урока {lesson_id}, завершаем генерацию курса"
                        )
                        if sid:
                            await redis.clear_course_generation_in_progress(sid)
        return content_list
    except Exception as e:
        log.exception(
            f"[generate_lesson_plan] Ошибка при генерации урока для sid={sid}: {e}"
        )
        await push_and_publish(
            _msg("bot", f"Произошла ошибка при создании урока: {str(e)}", "error"),
            sid,
        )
        await push_and_publish(
            _msg("system", "Ошибка при создании урока", "lesson_creation_error"),
            sid,
        )
        if sid:
            await redis.clear_course_generation_in_progress(sid)
        raise
