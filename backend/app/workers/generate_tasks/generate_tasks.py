import enum
import logging

from models.task import TaskTypeEnum
from schemas.task import TaskIn, TaskOut
from services.task_service.service import TaskService
from utils.uow import uow_context

log = logging.getLogger(__name__)


class GenerateDeepEnum(enum.Enum):
    user_summary = "user_summary"
    course = "course"
    module = "module"
    lesson = "lesson"
    first_lesson = "first_lesson"
    content = "content"


async def generate(ctx, task_type: str, **kwargs) -> TaskOut:

    async with uow_context() as uow:
        await TaskService(uow).create_task(
            TaskIn(id=ctx["job_id"], task_type=task_type.value, params=kwargs)
        )

    generate_tasks_context = {
        "main_task_id": ctx["job_id"],
        "parent_task_id": ctx["job_id"],
        "task_type": task_type.value,
        "params": kwargs,
    }

    if (
        task_type == TaskTypeEnum.generate_user_summary
        and kwargs.get("deep") != GenerateDeepEnum.user_summary.value
    ):
        audit_history = kwargs.get("audit_history")
        if not audit_history:
            log.error(f"Task with type generate_user_summary requires audit_history")
            return "Task with type generate_user_summary requires audit_history"
        await ctx["arq_queue"].enqueue_job(
            "generate_user_summary",
            audit_history=audit_history,
            generate_tasks_context=generate_tasks_context,
            _queue_name="course_generation",
        )

    elif (
        task_type == TaskTypeEnum.generate_course
        and kwargs.get("deep") != GenerateDeepEnum.course.value
    ):
        audit_history = kwargs.get("audit_history")
        if not audit_history:
            log.error(f"Task with type generate_user_summary requires audit_history")
            return "Task with type generate_user_summary requires audit_history"
        await ctx["arq_queue"].enqueue_job(
            "generate_user_summary",
            audit_history=audit_history,
            generate_tasks_context=generate_tasks_context,
            _queue_name="course_generation",
        )

    elif (
        task_type == TaskTypeEnum.generate_course
        and kwargs.get("deep") == GenerateDeepEnum.course.value
    ):
        user_pref = kwargs.get("user_pref")
        if not user_pref:
            log.error(f"Task with type generate_course requires user_pref")
            return "Task with type generate_course requires user_pref"
        await ctx["arq_queue"].enqueue_job(
            "generate_course_by_user_preference",
            generate_tasks_context=generate_tasks_context,
            user_pref=kwargs.get("user_pref"),
            _queue_name="course_generation",
        )

    elif task_type == TaskTypeEnum.generate_module:
        module_id = kwargs.get("module_id")
        if not module_id:
            return "Task with type generate_module requires module_id"
        await ctx["arq_queue"].enqueue_job(
            "generate_module",
            generate_tasks_context=generate_tasks_context,
            **kwargs,
            _queue_name="course_generation",
        )

    elif task_type == TaskTypeEnum.generate_lesson:
        lesson_id = kwargs.get("lesson_id")
        user_preferences = kwargs.get("user_preferences")
        if not lesson_id or not user_preferences:
            return (
                "Task with type generate_lesson requires lesson_id and user_preferences"
            )
        await ctx["arq_queue"].enqueue_job(
            "generate_lesson",
            lesson_id=lesson_id,
            user_preferences=user_preferences,
            generate_tasks_context=generate_tasks_context,
            _queue_name="course_generation",
        )

    elif task_type == TaskTypeEnum.generate_content:
        content_id = kwargs.get("content_id")
        if not content_id:
            return "Task with type generate_content requires content_id"
        await ctx["arq_queue"].enqueue_job(
            "generate_content",
            content_id=content_id,
            generate_tasks_context=generate_tasks_context,
            _queue_name="course_generation",
        )

    return None
