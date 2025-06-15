import uuid

from fastapi import APIRouter, Depends, HTTPException
from models.base import UserModel
from schemas import CourseOut, LessonOut
from services.learning_service.service import LearningService
from utils.auth_utils import is_user
from utils.uow import UnitOfWork, get_uow

courses_router = APIRouter(tags=["learning"])


@courses_router.get("/user-courses", response_model=list[CourseOut])
async def get_user_courses(
    current_user: UserModel = is_user,
    uow: UnitOfWork = Depends(get_uow),
):
    courses = await uow.learning_repo.get_courses_by_user_id(current_user.id)
    return courses


@courses_router.get("/course/{course_id}", response_model=CourseOut)
async def get_course_by_id(
    course_id: uuid.UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user: UserModel = is_user,
):
    service = LearningService(uow)
    course = await service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    if course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому курсу")

    return course


@courses_router.get("/course/{course_id}/lesson/{lesson_id}", response_model=LessonOut)
async def get_lesson_by_id(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    uow: UnitOfWork = Depends(get_uow),
    current_user: UserModel = is_user,
):
    service = LearningService(uow)
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson or (lesson.module and lesson.module.course_id != course_id):
        raise HTTPException(status_code=404, detail="Урок не найден в данном курсе")
    if lesson.module.course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому уроку")
    return lesson
