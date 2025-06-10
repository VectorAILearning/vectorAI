import logging
import uuid

from schemas.course import LessonOut
from schemas.generate import GenerateDeepEnum, GenerateTaskContext
from services.learning_service.service import LearningService
from utils import uow_context
from workers.generate_tasks.helpers import (
    _fail_task,
    _finish_course_generation_session,
    _finish_task,
    _next_module_or_first_lesson,
    _spawn_lesson_content_plan_task,
    _spawn_module_plan_task,
    _start_task,
)

log = logging.getLogger(__name__)


async def generate_module_plan(
    ctx,
    module_id: uuid.UUID,
    user_pref_summary: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    generate_tasks_context: GenerateTaskContext | None = None,
) -> list[LessonOut]:
    try:
        # ── генерируем уроки в модуле ─────────────────────────────────
        async with uow_context() as uow:
            await _start_task(uow, ctx["job_id"])

            lessons = await LearningService(uow).create_lessons_plan_by_module_id(
                module_id, user_pref_summary
            )
            await _finish_task(
                uow,
                ctx["job_id"],
                [LessonOut.model_validate(l).model_dump_json() for l in lessons],
            )

        if not generate_tasks_context:
            return [LessonOut.model_validate(l) for l in lessons]

        # ── следующий модуль или первый урок курса ────────────────────
        next_target = await _next_module_or_first_lesson(module_id)

        if isinstance(next_target, uuid.UUID):
            await _spawn_module_plan_task(
                ctx,
                next_target,
                user_pref_summary,
                session_id,
                user_id,
                generate_tasks_context,
                ctx["job_id"],
            )
        elif isinstance(next_target, tuple):
            lesson_id, _ = next_target
            await _spawn_lesson_content_plan_task(
                ctx,
                lesson_id,
                user_pref_summary,
                session_id,
                user_id,
                generate_tasks_context,
                ctx["job_id"],
            )

        return [LessonOut.model_validate(l) for l in lessons]

    except Exception as e:
        await _fail_task(ctx["job_id"], str(e))
        raise
