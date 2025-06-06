import logging

from models.course import ModuleModel
from models.task import TaskTypeEnum
from schemas.task import TaskIn
from services import get_cache_service
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from sqlalchemy import select
from utils.uow import uow_context
from workers.generate_tasks.audit_tasks import _msg
from workers.generate_tasks.generate_tasks import GenerateDeepEnum

log = logging.getLogger(__name__)


async def generate_module_plan(
    ctx, course_id: str, user_pref_summary: str, generate_tasks_context: dict
) -> list[ModuleModel]:
    """
    Генерация плана модулей на основе структуры курса и предпочтений пользователя.
    Args:
        ctx: контекст
        course_id: id курса
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        list[ModuleModel]: список модулей
    """
    sid = generate_tasks_context["params"].get("sid")
    user_id = generate_tasks_context["params"].get("user_id")
    generate_params = generate_tasks_context["params"]
    generate_tasks_context["task_type"] = TaskTypeEnum.generate_module_plan.value

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
            # await push_and_publish(_msg("bot", "Генерируем план модулей курса…"), sid)

            modules = await LearningService(uow).create_modules_plan_by_course_id(
                course_id, user_pref_summary
            )

            # await push_and_publish(_msg("bot", "План модулей сгенерирован!"), sid)

        if (
            generate_tasks_context["main_task_type"]
            == TaskTypeEnum.generate_course.value
        ):
            if generate_params.get("deep") != GenerateDeepEnum.course.value:
                first_module = min(modules, key=lambda m: m.position)
                await ctx["arq_queue"].enqueue_job(
                    "generate_module",
                    str(first_module.id),
                    user_pref_summary,
                    generate_tasks_context,
                    _queue_name="course_generation",
                )

        return modules
    except Exception as e:
        log.exception(
            f"[generate_module_plan] Ошибка при генерации плана модулей для sid={sid}: {e}"
        )
        await push_and_publish(
            _msg(
                "bot", f"Произошла ошибка при создании плана модулей: {str(e)}", "error"
            ),
            sid,
        )
        await push_and_publish(
            _msg(
                "system",
                "Ошибка при создании плана модулей",
                "module_plan_creation_error",
            ),
            sid,
        )
        if sid:
            await redis.clear_course_generation_in_progress(sid)
        raise


async def generate_module(
    ctx, module_id: str, user_pref_summary: str, generate_tasks_context: dict
) -> ModuleModel:
    """
    Генерация модуля на основе предпочтений пользователя.
    Args:
        ctx: контекст
        module_id: id модуля
        user_pref_summary: предпочтения пользователя
        generate_tasks_context: контекст задач генераций
    Returns:
        ModuleModel: модуль
    """
    sid = generate_tasks_context["params"].get("sid")
    user_id = generate_tasks_context["params"].get("user_id")
    generate_params = generate_tasks_context["params"]
    generate_tasks_context["task_type"] = TaskTypeEnum.generate_module.value

    log.info(f"[generate_module] Генерация модуля {module_id} для sid={sid}")

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
            module = await LearningService(uow).get_module_by_id(module_id)

            # await push_and_publish(_msg("bot", f"Генерируем план уроков для модуля {module.title}…"), sid)

            lessons = await LearningService(uow).create_lessons_plan_by_module_id(
                module_id, user_pref_summary
            )

            log.info(
                f"[generate_module] План уроков для модуля {module.title} сгенерирован"
            )
            # await push_and_publish(_msg("bot", f"План уроков для модуля {module.title} сгенерирован!"), sid)

            if (
                generate_tasks_context["main_task_type"]
                == TaskTypeEnum.generate_course.value
            ):
                if generate_params.get("deep") != GenerateDeepEnum.module.value:
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
                        await ctx["arq_queue"].enqueue_job(
                            "generate_module",
                            str(next_module.id),
                            user_pref_summary,
                            generate_tasks_context,
                            _queue_name="course_generation",
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
                        await ctx["arq_queue"].enqueue_job(
                            "generate_lesson_plan",
                            str(first_lesson.id),
                            user_pref_summary,
                            generate_tasks_context,
                            _queue_name="course_generation",
                        )
            return lessons
    except Exception as e:
        log.exception(
            f"[generate_module] Ошибка при генерации модуля для sid={sid}: {e}"
        )
        await push_and_publish(
            _msg("bot", f"Произошла ошибка при создании модуля: {str(e)}", "error"),
            sid,
        )
        await push_and_publish(
            _msg("system", "Ошибка при создании модуля", "module_creation_error"),
            sid,
        )
        if sid:
            await redis.clear_course_generation_in_progress(sid)
        raise
