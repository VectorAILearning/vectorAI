import uuid
from fastapi import APIRouter, Depends, HTTPException
from services.learning_service.service import LearningService
from utils.uow import UnitOfWork, get_uow

lessons_router = APIRouter(tags=["lessons"])

@lessons_router.post("/lesson/{lesson_id}/generate-content")
async def generate_lesson_content(
    lesson_id: uuid.UUID,
    uow: UnitOfWork = Depends(get_uow),
):
    service = LearningService(uow)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    if hasattr(lesson, "contents") and lesson.contents and len(lesson.contents) > 0:
        raise HTTPException(status_code=400, detail="Контент для этого урока уже сгенерирован")

    course = lesson.module.course if lesson.module else None
    user_preferences = ""
    if course and course.preference and course.preference.summary:
        user_preferences = course.preference.summary

    content = await service.generate_and_save_lesson_content(lesson, user_preferences)
    return {"lesson_id": str(lesson_id), "content": content}

@lessons_router.post("/lesson/{lesson_id}/regenerate-content")
async def regenerate_lesson_content(
    lesson_id: uuid.UUID,
    uow: UnitOfWork = Depends(get_uow),
):
    service = LearningService(uow)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    db = uow.session
    for content in list(lesson.contents):
        await db.delete(content)
    await db.commit()

    course = lesson.module.course if lesson.module else None
    user_preferences = ""
    if course and course.preference and course.preference.summary:
        user_preferences = course.preference.summary

    content = await service.generate_and_save_lesson_content(lesson, user_preferences)
    return {"lesson_id": str(lesson_id), "content": content} 