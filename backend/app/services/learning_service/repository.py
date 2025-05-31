import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from schemas import CourseIn
from models import CourseModel, ModuleModel, LessonModel


class LearningRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_course_by_json(
        self,
        course_json: dict,
        user_id: str = None,
        session_id: str = None,
    ) -> CourseModel:
        course_in = CourseIn(**course_json)

        course = CourseModel(
            title=course_in.course_title,
            description=course_in.course_description,
            estimated_time_hours=course_in.estimated_time_hours,
            user_id=uuid.UUID(user_id) if user_id else None,
            session_id=uuid.UUID(session_id) if session_id else None,
            modules=[
                ModuleModel(
                    title=mod.title,
                    description=mod.description,
                    estimated_time_hours=mod.estimated_time_hours,
                    lessons=[
                        LessonModel(
                            title=les.title,
                            description=les.description,
                            estimated_time_hours=les.estimated_time_hours,
                        )
                        for les in mod.lessons
                    ],
                )
                for mod in course_in.modules
            ],
        )
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)

        return course
