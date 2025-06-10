import logging
import uuid

from schemas.course import ContentOut
from schemas.generate import GenerateTaskContext
from services.content_service.service import ContentService
from utils import uow_context
from workers.generate_tasks.helpers import (
    _fail_course_generation_session,
    _fail_task,
    _find_next_content_block,
    _finish_course_generation_session,
    _finish_task,
    _spawn_generate_content_task,
    _start_task,
)

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
    Генерирует content для блока урока и цепляет следующую задачу, если нужно.
    """
    try:
        async with uow_context() as uow:
            await _start_task(uow, ctx["job_id"])

            content_block = await uow.content_repo.get_content_by_id(content_block_id)
            if not content_block:
                raise ValueError(f"Блок контента {content_block_id} не найден")

            lesson = content_block.lesson
            if not lesson:
                raise ValueError(f"Урок {lesson_id} не найден")

            # ─── генерируем «мясо» блока ────────────────────────────────
            await ContentService(uow).generate_content_by_block(content_block)

            # ─── ищем, что генерировать дальше ─────────────────────────
            next_block = await _find_next_content_block(
                content_block, generate_tasks_context
            )
            if next_block:
                await _spawn_generate_content_task(
                    ctx,
                    next_block.id,
                    lesson_id,
                    user_pref_summary,
                    session_id,
                    user_id,
                    ctx["job_id"],
                    generate_tasks_context,
                )
            else:
                # курс/модуль/урок закончились
                if generate_tasks_context and generate_tasks_context.main_task_id:
                    await _finish_task(
                        uow,
                        generate_tasks_context.main_task_id,
                        "course_generation_done",
                    )
                    await _finish_course_generation_session(session_id)

            # ─── отмечаем текущую задачу «success» ─────────────────────
            result_json = ContentOut.model_validate(content_block).model_dump_json()
            await _finish_task(uow, ctx["job_id"], result_json)

            return ContentOut.model_validate(content_block)

    except Exception as e:
        # глобальный фолбэк-обработчик
        await _fail_course_generation_session(session_id)
        await _fail_task(ctx["job_id"], str(e))
        if generate_tasks_context and generate_tasks_context.main_task_id:
            await _fail_task(generate_tasks_context.main_task_id, str(e))
        raise
