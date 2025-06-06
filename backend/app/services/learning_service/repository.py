import logging
import uuid

from fastapi import HTTPException
from models import CourseModel, LessonModel, ModuleModel
from models.content import ContentModel
from schemas import CourseIn, CourseUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

log = logging.getLogger(__name__)


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

    async def get_module_by_id(self, module_id: uuid.UUID) -> ModuleModel | None:
        stmt = (
            select(ModuleModel)
            .where(ModuleModel.id == module_id)
            .options(
                selectinload(ModuleModel.lessons),
                selectinload(ModuleModel.course)
                .selectinload(CourseModel.modules)
                .selectinload(ModuleModel.lessons)
                .selectinload(LessonModel.contents),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_module_by_json(
        self,
        module_json: dict,
        course_id: uuid.UUID,
    ) -> ModuleModel:
        log.info(f"Module json: {module_json}")
        module = ModuleModel(
            title=module_json["title"],
            description=module_json["description"],
            estimated_time_hours=module_json["estimated_time_hours"],
            position=module_json["position"],
            course_id=course_id,
        )
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def get_lesson_by_id(self, lesson_id: uuid.UUID) -> LessonModel | None:
        stmt = (
            select(LessonModel)
            .where(LessonModel.id == lesson_id)
            .options(
                selectinload(LessonModel.module)
                .selectinload(ModuleModel.course)
                .selectinload(CourseModel.modules)
                .selectinload(ModuleModel.lessons)
                .selectinload(LessonModel.contents),
                selectinload(LessonModel.contents),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_lesson_by_json(
        self,
        lesson_json: dict,
        module_id: uuid.UUID,
    ) -> LessonModel:
        lesson = LessonModel(
            title=lesson_json["title"],
            description=lesson_json["description"],
            estimated_time_hours=lesson_json["estimated_time_hours"],
            position=lesson_json["position"],
            module_id=module_id,
        )
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)
        return lesson

    async def get_content_by_id(self, content_id: uuid.UUID) -> ContentModel | None:
        stmt = select(ContentModel).where(ContentModel.id == content_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
