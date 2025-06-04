import uuid
import json

from agents.lesson_agent.agent import LessonPlanAgent
from agents.plan_agent.agent import CoursePlanAgent
from models.course import LessonModel
from models import ContentModel, CourseModel, PreferenceModel
from models.content import ContentType
from schemas import CourseUpdate, PreferenceUpdate
from utils.uow import UnitOfWork
from schemas.course import CourseOut, ContentOut
from pydantic import ValidationError


class LearningService:
    def __init__(self, uow: UnitOfWork, agent: CoursePlanAgent | None = None):
        self.agent = agent or CoursePlanAgent()
        self.uow = uow

    async def create_course_by_user_preference(
        self, preference: PreferenceModel, sid: str
    ) -> CourseModel:
        course_plan = self.agent.generate_course(preference.summary)
        course = await self.uow.learning_repo.create_course_by_json(
            course_plan, session_id=sid
        )
        await self.uow.audit_repo.update_course_preference(
            preference.id, PreferenceUpdate(course_id=course.id)
        )
        return course

    async def initiate_user_learning_by_session_id(
        self, user_id: uuid.UUID, session_id: uuid.UUID
    ):
        course = await self.uow.learning_repo.get_course_by_session_id(session_id)
        if not course:
            return

        await self.uow.learning_repo.update_course(
            data=CourseUpdate(user_id=user_id),
            course_id=course.id,
        )
        await self.uow.audit_repo.update_course_preference(
            data=PreferenceUpdate(user_id=user_id), preference_id=course.preference.id
        )

    async def get_course_by_id(self, course_id: uuid.UUID):
        return await self.uow.learning_repo.get_course_by_id(course_id)

    async def get_lesson_by_id(self, lesson_id: uuid.UUID):
        return await self.uow.learning_repo.get_lesson_by_id(lesson_id)

    async def generate_and_save_lesson_content_plan(
        self, lesson: LessonModel, user_preferences: str = ""
    ) -> list[ContentModel]:
        course_dict = CourseOut.model_validate(lesson.module.course).model_dump()
        content_plan = LessonPlanAgent().generate_lesson_content_plan(
            lesson_description=f"{lesson.title}. {lesson.description}. Цель: {lesson.goal}",
            user_preferences=user_preferences,
            course_structure_json=json.dumps(course_dict, ensure_ascii=False, default=str),
        )
        if not isinstance(content_plan, list):
            raise ValueError(f"Генерация вернула не список блоков. Ответ: {content_plan}")
        
        content_list = []
        
        for block in content_plan:
            try:
                content_obj = ContentOut.model_validate(block)
            except ValidationError as e:
                raise ValueError(f"Некорректный формат блока: {e}")
            db_content = ContentModel(
                lesson_id=lesson.id,
                type=ContentType(content_obj.type),
                description=content_obj.description,
                goal=content_obj.goal,
                content=content_obj.content,
                position=content_obj.position,
            )
            self.uow.session.add(db_content)
            content_list.append(db_content)
        
        await self.uow.session.commit()
        for db_content in content_list:
            await self.uow.session.refresh(db_content)
        return content_list
