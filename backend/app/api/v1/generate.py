import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.task import TaskTypeEnum
from schemas.generate import GenerateDeepEnum
from schemas.task import TaskIn, TaskOut
from services.learning_service.service import LearningService
from services.session_service.service import SessionService
from services.task_service.service import TaskService
from utils.uow import UnitOfWork, get_uow

generate_router = APIRouter(tags=["generate"])


@generate_router.post("/lesson/{lesson_id}/generate-content", response_model=TaskOut)
async def generate_lesson_content(
    lesson_id: uuid.UUID,
    request: Request,
    force: bool = Query(
        False, description="Перегенерировать контент, если уже существует"
    ),
    uow: UnitOfWork = Depends(get_uow),
):
    session_id = await SessionService(uow).get_session_id_by_request(request)

    lesson = await LearningService(uow).get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    if lesson.contents and len(lesson.contents) > 0:
        if not force:
            raise HTTPException(
                status_code=400, detail="Контент для этого урока уже сгенерирован"
            )
        for content in lesson.contents:
            await uow.session.delete(content)

    user_preferences = lesson.module.course.preference.summary

    job = await request.app.state.arq_pool.enqueue_job(
        "generate_lesson",
        _queue_name="course_generation",
        lesson_id=lesson_id,
        user_pref_summary=user_preferences,
        session_id=session_id,
    )

    task = await TaskService(uow).create_task(
        TaskIn(
            id=job.job_id,
            task_type=TaskTypeEnum.generate_lesson,
            params={
                "lesson_id": str(lesson_id),
                "deep": GenerateDeepEnum.lesson_content.value,
                "user_pref_summary": user_preferences,
            },
            session_id=uuid.UUID(session_id) if session_id else None,
        )
    )

    return task
