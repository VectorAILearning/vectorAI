import logging
import uuid

from models.task import TaskTypeEnum
from schemas.course import CourseOut, ModuleOut
from schemas.generate import GenerateDeepEnum, GenerateTaskContext
from schemas.task import TaskIn, TaskOut
from services.learning_service.service import LearningService
from services.message_bus import push_and_publish
from services.task_service.service import TaskService
from utils import _msg, uow_context
from workers.generate_tasks.helpers import (
    _fail_course_generation_session,
    _fail_task,
    _finish_course_generation_session,
    _finish_task,
    _spawn_course_plan_task,
    _spawn_module_plan_task,
    _spawn_user_summary_task,
    _start_task,
)

log = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────
# TOP-LEVEL: полный курс
# ────────────────────────────────────────────────────────────────────────
async def generate_course(
    ctx,
    audit_history: str,
    deep: str,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> TaskOut:
    gctx = GenerateTaskContext(
        main_task_id=ctx["job_id"],
        main_task_type=TaskTypeEnum.generate_course,
        deep=deep,
        session_id=session_id,
        user_id=user_id,
    )
    try:
        async with uow_context() as uow:
            await _start_task(uow, ctx["job_id"])

            task_db = await _spawn_user_summary_task(
                ctx, audit_history, session_id, user_id, gctx, ctx["job_id"]
            )

            await push_and_publish(
                _msg("bot", "Генерируем для вас индивидуальный курс…", "chat_info"),
                session_id,
            )
            return task_db
    except Exception as e:
        await _fail_task(ctx["job_id"], str(e))
        await _fail_course_generation_session(session_id)
        raise


# ────────────────────────────────────────────────────────────────────────
# STEP 1: базовые поля курса
# ────────────────────────────────────────────────────────────────────────
async def generate_course_base(
    ctx,
    user_pref_id: uuid.UUID,
    generate_tasks_context: GenerateTaskContext,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> CourseOut:
    try:
        async with uow_context() as uow:
            await _start_task(uow, ctx["job_id"])

            pref = await uow.audit_repo.get_by_id(user_pref_id)
            if not pref:
                raise ValueError("preference not found")

            course = await LearningService(uow).create_course_by_user_preference(
                pref, sid=session_id, user_id=user_id
            )
            await _finish_task(
                uow, ctx["job_id"], CourseOut.model_validate(course).model_dump_json()
            )

            await push_and_publish(
                _msg("bot", "Структура курса сгенерирована!", "course_generation_done"),
                session_id,
            )
            await _finish_course_generation_session(session_id)

            if (
                generate_tasks_context
                and generate_tasks_context.deep != GenerateDeepEnum.course_base.value
            ):
                await _spawn_course_plan_task(
                    ctx,
                    course.id,
                    pref.summary,
                    generate_tasks_context,
                    session_id,
                    user_id,
                    ctx["job_id"],
                )
        return CourseOut.model_validate(course)
    except Exception as e:
        await _fail_task(ctx["job_id"], str(e))
        await _fail_course_generation_session(session_id)
        raise


# ────────────────────────────────────────────────────────────────────────
# STEP 2: план модулей
# ────────────────────────────────────────────────────────────────────────
async def generate_course_plan(
    ctx,
    course_id: uuid.UUID,
    user_pref_summary: str,
    generate_tasks_context: GenerateTaskContext,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> list[ModuleOut]:
    try:
        async with uow_context() as uow:
            await _start_task(uow, ctx["job_id"])
            modules = await LearningService(uow).create_modules_plan_by_course_id(
                course_id, user_pref_summary
            )
            await _finish_task(
                uow,
                ctx["job_id"],
                [ModuleOut.model_validate(m).model_dump_json() for m in modules],
            )

        # запускаем следующий шаг
        if (
            generate_tasks_context
            and generate_tasks_context.deep != GenerateDeepEnum.course_plan.value
        ):
            first_module = min(modules, key=lambda m: m.position)
            await _spawn_module_plan_task(
                ctx,
                first_module.id,
                user_pref_summary,
                generate_tasks_context,
                session_id,
                user_id,
                ctx["job_id"],
            )

        return [ModuleOut.model_validate(m) for m in modules]
    except Exception as e:
        await _fail_task(ctx["job_id"], str(e))
        await _fail_course_generation_session(session_id)
        raise
