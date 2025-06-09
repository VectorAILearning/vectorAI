import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from services.learning_service.service import LearningService
from utils.uow import UnitOfWork, get_uow

generate_router = APIRouter(tags=["generate"])


@generate_router.post("/lesson/{lesson_id}/generate-content")
async def generate_lesson_content(
    lesson_id: uuid.UUID,
    force: bool = Query(
        False, description="Перегенерировать контент, если уже существует"
    ),
    uow: UnitOfWork = Depends(get_uow),
):
    service = LearningService(uow)
    lesson = await service.get_lesson_by_id(lesson_id)
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

    content = await service.generate_and_save_lesson_content_plan(
        lesson, user_preferences
    )
    return {"lesson_id": str(lesson_id), "content": content}
