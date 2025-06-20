import logging
import uuid

from core.database import get_async_session_generator
from models.task import TaskTypeEnum
from schemas.course import ContentOut
from schemas.generate import GenerateDeepEnum, GenerateTaskContext
from schemas.task import TaskIn, TaskOut
from services.learning_service.service import get_learning_service
from services.task_service.service import get_task_service
from workers.generate_tasks.helpers import (
    _enqueue_next_lesson_plan_task,
    _fail_course_generation_session,
    _fail_task,
    _finish_task,
    _spawn_generate_content_task,
    _start_task,
)

log = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────
# STEP 0: entry-point «урок целиком»
# ────────────────────────────────────────────────────────────────────────
async def generate_lesson(
    ctx,
    lesson_id: uuid.UUID,
    user_pref_summary: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> TaskOut:
    gctx = GenerateTaskContext(
        main_task_id=ctx["job_id"],
        main_task_type=TaskTypeEnum.generate_lesson,
        deep=GenerateDeepEnum.lesson_content.value,
        session_id=session_id,
        user_id=user_id,
    )
    async with get_async_session_generator() as async_session:
        await _start_task(async_session, ctx["job_id"])

        job = await ctx["arq_queue"].enqueue_job(
            "generate_lesson_content_plan",
            lesson_id,
            user_pref_summary,
            gctx,
            session_id,
            user_id,
            _queue_name="course_generation",
        )

        task_service = get_task_service(async_session)
        return await task_service.create_task(
            TaskIn(
                id=job.job_id,
                task_type=TaskTypeEnum.generate_lesson_content_plan,
                params={"lesson_id": str(lesson_id)},
                session_id=session_id,
                user_id=user_id,
                parent_id=ctx["job_id"],
            )
        )


# ────────────────────────────────────────────────────────────────────────
# STEP 1: контент-план урока
# ────────────────────────────────────────────────────────────────────────
async def generate_lesson_content_plan(
    ctx,
    lesson_id: uuid.UUID,
    user_pref_summary: str,
    generate_tasks_context: GenerateTaskContext,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> list[ContentOut]:
    try:
        # ── планируем блоки ────────────────────────────────────────────
        async with get_async_session_generator() as async_session:
            await _start_task(async_session, ctx["job_id"])
            learning_service = get_learning_service(async_session)
            lesson = await learning_service.get_lesson_by_id(lesson_id)
            content_blocks = (
                await learning_service.generate_and_save_lesson_content_plan(
                    lesson_id, user_pref_summary
                )
            )
            await _finish_task(
                async_session,
                ctx["job_id"],
                [
                    ContentOut.model_validate(b).model_dump_json()
                    for b in content_blocks
                ],
            )

        # ── решаем, что делать дальше ─────────────────────────────────
        # 1) сгенерировать контент первого блока
        if generate_tasks_context.deep in (
            GenerateDeepEnum.first_lesson_content.value,
            GenerateDeepEnum.lesson_content.value,
        ):
            first_block = min(content_blocks, key=lambda b: b.position)
            await _spawn_generate_content_task(
                ctx,
                first_block.id,
                lesson_id,
                user_pref_summary,
                generate_tasks_context,
                session_id,
                user_id,
                ctx["job_id"],
            )
            return [ContentOut.model_validate(b) for b in content_blocks]

        # 2) перейти к следующему уроку / модулю, если нужно
        await _enqueue_next_lesson_plan_task(
            ctx,
            lesson,
            user_pref_summary,
            session_id,
            user_id,
            generate_tasks_context,
            parent_id=ctx["job_id"],
        )
        return [ContentOut.model_validate(b) for b in content_blocks]

    except Exception as e:
        await _fail_task(async_session, ctx["job_id"], str(e))
        await _fail_course_generation_session(session_id)
        raise
