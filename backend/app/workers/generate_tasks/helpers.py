# backend/app/workers/generate_tasks/helpers.py
import uuid
from datetime import datetime
from typing import Any, Iterable, Optional

from models.content import ContentModel
from models.task import TaskStatusEnum, TaskTypeEnum
from schemas.generate import GenerateDeepEnum, GenerateTaskContext
from schemas.task import TaskIn, TaskOut
from services import get_cache_service
from services.learning_service.service import LearningService
from services.task_service.service import TaskService
from utils.task_utils import wait_for_task_in_db
from utils.uow import UnitOfWork, uow_context

# ────────────────────────────────────────────────────────────────────────
# Task-flow helpers
# ────────────────────────────────────────────────────────────────────────


async def _start_task(uow: UnitOfWork, task_id: str) -> TaskOut:
    task = await wait_for_task_in_db(uow.task_repo, task_id)
    if not task:
        raise Exception(f"Task {task_id} not found in DB")
    task.status = TaskStatusEnum.in_progress
    task.started_at = datetime.now()
    return await TaskService(uow).update_task(task)


async def _finish_task(uow: UnitOfWork, task_id: str, result: Any) -> TaskOut:
    task = await wait_for_task_in_db(uow.task_repo, task_id)
    if not task:
        raise Exception(f"Task {task_id} not found in DB")
    task.status = TaskStatusEnum.success
    task.result = result
    task.finished_at = datetime.now()
    return await TaskService(uow).update_task(task)


async def _fail_task(task_id: str, error_message: str) -> TaskOut:
    async with uow_context() as uow:
        task = await wait_for_task_in_db(uow.task_repo, task_id)
        if not task:
            raise Exception(f"Task {task_id} not found in DB")
        task.status = TaskStatusEnum.failed
        task.error_message = error_message
        task.finished_at = datetime.now()
        return await TaskService(uow).update_task(task)


# ────────────────────────────────────────────────────────────────────────
# Навигация по контенту
# ────────────────────────────────────────────────────────────────────────


def _first_by_position(items: Iterable) -> Optional[Any]:
    return min(items, key=lambda x: x.position) if items else None


async def _find_next_content_block(
    block: ContentModel,
    ctx: GenerateTaskContext | None,
) -> Optional[ContentModel]:
    lesson = block.lesson

    # следующий блок в том же уроке
    nxt = next((b for b in lesson.contents if b.position > block.position), None)
    if nxt:
        return nxt

    # если deep ограничивает, дальше не идём
    if ctx and ctx.deep in (
        GenerateDeepEnum.first_lesson_content.value,
        GenerateDeepEnum.lesson_content.value,
    ):
        return None

    # первый блок следующего урока
    next_lesson = next(
        (l for l in lesson.module.lessons if l.position > lesson.position), None
    )
    if next_lesson:
        return _first_by_position(next_lesson.contents)

    # первый блок первого урока следующего модуля
    next_module = next(
        (
            m
            for m in lesson.module.course.modules
            if m.position > lesson.module.position
        ),
        None,
    )
    if next_module:
        first_lesson = _first_by_position(next_module.lessons)
        if first_lesson:
            return _first_by_position(first_lesson.contents)

    return None


async def _finish_course_generation_session(session_id: str | uuid.UUID | None) -> None:
    if not session_id:
        return
    redis = get_cache_service()
    await redis.clear_course_generation_in_progress(str(session_id))
    await redis.set_session_status(str(session_id), "course_generation_done")


async def _fail_course_generation_session(session_id: str | uuid.UUID | None) -> None:
    if not session_id:
        return
    redis = get_cache_service()
    await redis.clear_course_generation_in_progress(str(session_id))
    await redis.set_session_status(str(session_id), "course_generation_error")


async def _enqueue_next_lesson_plan_task(
    ctx,
    lesson,
    user_pref_summary,
    session_id,
    user_id,
    gctx: GenerateTaskContext,
    parent_id: str,
):
    # следующий урок в модуле
    next_lesson = next(
        (l for l in lesson.module.lessons if l.position > lesson.position), None
    )
    if next_lesson:
        await _spawn_lesson_content_plan_task(
            ctx, next_lesson.id, user_pref_summary, session_id, user_id, gctx, parent_id
        )
        return

    # первый урок следующего модуля
    next_module = next(
        (
            m
            for m in lesson.module.course.modules
            if m.position > lesson.module.position
        ),
        None,
    )
    if next_module and next_module.lessons:
        first_lesson = min(next_module.lessons, key=lambda l: l.position)
        await _spawn_lesson_content_plan_task(
            ctx,
            first_lesson.id,
            user_pref_summary,
            session_id,
            user_id,
            gctx,
            parent_id,
        )
        return


async def _next_module_or_first_lesson(module_id: uuid.UUID):
    async with uow_context() as uow:
        module = await LearningService(uow).get_module_by_id(module_id)
        if not module:
            return None

        next_mod = next(
            (m for m in module.course.modules if m.position > module.position), None
        )
        if next_mod:
            return next_mod.id

        first_module = await LearningService(uow).get_first_module_by_course_id(
            module.course.id
        )

        first_lesson = min(first_module.lessons, key=lambda l: l.position)
        if not first_lesson:
            return None

        return (first_lesson.id, None)


async def _spawn_module_plan_task(ctx, mod_id, pref, sid, uid, gctx, parent):
    job = await ctx["arq_queue"].enqueue_job(
        "generate_module_plan",
        mod_id,
        pref,
        sid,
        uid,
        gctx,
        _queue_name="course_generation",
    )
    async with uow_context() as uow:
        await TaskService(uow).create_task(
            TaskIn(
                id=job.job_id,
                task_type=TaskTypeEnum.generate_module_plan,
                params={"module_id": str(mod_id)},
                session_id=sid,
                user_id=uid,
                parent_id=parent,
            )
        )


async def _spawn_lesson_content_plan_task(
    ctx,
    lesson_id: uuid.UUID,
    user_pref_summary: str,
    session_id,
    user_id,
    gctx: GenerateTaskContext,
    parent_id: str,
):
    job = await ctx["arq_queue"].enqueue_job(
        "generate_lesson_content_plan",
        lesson_id,
        user_pref_summary,
        session_id,
        user_id,
        gctx,
        _queue_name="course_generation",
    )
    async with uow_context() as uow:
        await TaskService(uow).create_task(
            TaskIn(
                id=job.job_id,
                task_type=TaskTypeEnum.generate_lesson_content_plan,
                params={"lesson_id": str(lesson_id)},
                session_id=session_id,
                user_id=user_id,
                parent_id=uuid.UUID(parent_id),
            )
        )


async def _spawn_generate_content_task(
    ctx,
    block_id: uuid.UUID,
    lesson_id: uuid.UUID,
    user_pref_summary: str,
    session_id,
    user_id,
    parent_id: str,
    gctx: GenerateTaskContext | None = None,
):
    job = await ctx["arq_queue"].enqueue_job(
        "generate_content",
        block_id,
        lesson_id,
        user_pref_summary,
        session_id,
        user_id,
        gctx,
        _queue_name="course_generation",
    )
    async with uow_context() as uow:
        await TaskService(uow).create_task(
            TaskIn(
                id=job.job_id,
                task_type=TaskTypeEnum.generate_content,
                params={"content_block_id": str(block_id)},
                session_id=session_id,
                user_id=user_id,
                parent_id=uuid.UUID(parent_id),
            )
        )
