from core.database import db_helper
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models import CourseModel
from models.base import UserModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

courses_router = APIRouter()


@courses_router.get("/user-courses", response_class=JSONResponse)
async def get_user_courses(
    username: str = "test", db: AsyncSession = Depends(db_helper.get_session)
):
    # user_stmt = await db.execute(
    #     select(UserModel).where(UserModel.username == username)
    # )
    # user = user_stmt.scalar_one_or_none()
    # if not user:
    #     return JSONResponse(content={"courses": []})

    courses_stmt = await db.execute(select(CourseModel))
    courses = courses_stmt.scalars().all()

    courses_json = []
    for course in courses:
        modules_json = []
        for module in course.modules:
            lessons_json = [
                {
                    "title": lesson.title,
                    "description": lesson.description,
                    "estimated_time_hours": lesson.estimated_time_hours,
                }
                for lesson in module.lessons
            ]
            modules_json.append(
                {
                    "title": module.title,
                    "description": module.description,
                    "estimated_time_hours": module.estimated_time_hours,
                    "lessons": lessons_json,
                }
            )
        courses_json.append(
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "estimated_time_hours": course.estimated_time_hours,
                "modules": modules_json,
            }
        )

    return JSONResponse(content={"courses": courses_json})
