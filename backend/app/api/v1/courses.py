import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from schemas import CourseOut, LessonOut
from services.learning_service.service import LearningService
from services.session_service.service import SessionService
from utils.uow import UnitOfWork, get_uow

courses_router = APIRouter(tags=["learning"])


@courses_router.get("/user-courses", response_model=list[CourseOut])
async def get_user_courses(request: Request, uow: UnitOfWork = Depends(get_uow)):
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    session_id = await SessionService(uow).get_session_id_by_ip_user_agent(
        ip, user_agent
    )
    courses = await uow.learning_repo.get_courses_by_session_id(session_id)
    return courses


@courses_router.get("/course/{course_id}", response_model=CourseOut)
async def get_course_by_id(course_id: uuid.UUID, uow: UnitOfWork = Depends(get_uow)):
    service = LearningService(uow)
    course = await service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


@courses_router.get("/course/{course_id}/lesson/{lesson_id}", response_model=LessonOut)
async def get_lesson_by_id(
    course_id: uuid.UUID, lesson_id: uuid.UUID, uow: UnitOfWork = Depends(get_uow)
):
    service = LearningService(uow)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson or (lesson.module and lesson.module.course_id != course_id):
        raise HTTPException(status_code=404, detail="Урок не найден в данном курсе")
    return lesson
