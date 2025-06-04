import uuid

from fastapi import HTTPException
from models import CourseModel, LessonModel, ModuleModel
from schemas import CourseIn, CourseUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


class LearningRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_course(
        self, course_id: uuid.UUID, data: CourseUpdate
    ) -> CourseModel:
        stmt = select(CourseModel).where(CourseModel.id == course_id)
        result = await self.db.execute(stmt)
        course = result.scalar_one_or_none()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(course, field, value)

        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def get_courses_by_session_id(
        self, session_id: str
    ) -> list[CourseModel | None]:
        stmt = select(CourseModel).where(CourseModel.session_id == session_id)
        result = await self.db.execute(stmt)
        courses = result.scalars()
        return list(courses)

    async def create_course_by_json(
        self,
        course_json: dict,
        user_id: str = None,
        session_id: str = None,
    ) -> CourseModel:
        course_in = CourseIn(**course_json)

        course = CourseModel(
            title=course_in.title,
            description=course_in.description,
            goal=course_in.goal,
            estimated_time_hours=course_in.estimated_time_hours,
            user_id=uuid.UUID(user_id) if user_id else None,
            session_id=uuid.UUID(session_id) if session_id else None,
            modules=[
                ModuleModel(
                    title=mod.title,
                    description=mod.description,
                    estimated_time_hours=mod.estimated_time_hours,
                    goal=mod.goal,
                    position=mod.position,
                    lessons=[
                        LessonModel(
                            title=les.title,
                            goal=les.goal,
                            position=les.position,
                            description=(
                                les.description
                            ),
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

    async def get_course_by_id(self, course_id: uuid.UUID) -> CourseModel | None:
        stmt = (
            select(CourseModel)
            .where(CourseModel.id == course_id)
            .options(
                selectinload(CourseModel.modules)
                .selectinload(ModuleModel.lessons)
                .selectinload(LessonModel.contents)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_lesson_by_id(self, lesson_id: uuid.UUID) -> LessonModel | None:
        stmt = (
            select(LessonModel)
            .where(LessonModel.id == lesson_id)
            .options(
                selectinload(LessonModel.module).selectinload(ModuleModel.course),
                selectinload(LessonModel.contents),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
