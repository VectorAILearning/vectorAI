import json
import logging
import uuid

from agents.plan_agent.agent import CoursePlanAgent
from models import ContentModel, CourseModel, PreferenceModel
from models.content import ContentType
from models.course import LessonModel, ModuleModel
from pydantic import ValidationError
from schemas import CourseUpdate, PreferenceUpdate
from schemas.course import (
    ContentOut,
    CourseOut,
    CourseStructureOut,
    CourseStructureWithModulesOut,
    LessonStructureOut,
    ModuleStructureOut,
    ModuleStructureWithLessonsOut,
)
from utils.uow import UnitOfWork

log = logging.getLogger(__name__)


class LearningService:
    def __init__(self, uow: UnitOfWork, agent: CoursePlanAgent | None = None):
        self.agent = agent or CoursePlanAgent()
        self.uow = uow

    async def create_course_by_user_preference(
        self,
        preference: PreferenceModel,
        sid: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ) -> CourseModel:
        course_plan = self.agent.generate_course_plan(preference.summary)
        log.info(f"Course plan: {course_plan}")
        course = await self.uow.learning_repo.create_course_by_json(
            course_plan, session_id=sid, user_id=user_id
        )
        await self.uow.audit_repo.update_course_preference(
            preference.id, PreferenceUpdate(course_id=course.id)
        )
        return course

    async def create_modules_plan_by_course_id(
        self, course_id: uuid.UUID, user_preferences: str
    ) -> list[ModuleModel]:
        course = await self.uow.learning_repo.get_course_by_id(course_id)
        course_structure_json = CourseStructureWithModulesOut.model_validate(
            course
        ).model_dump_json()
        module_plan = self.agent.generate_module_plan(
            course_structure_json=course_structure_json,
            user_preferences=user_preferences,
        )
        module_list = []
        for module_dict in module_plan:
            module = await self.uow.learning_repo.create_module_by_json(
                module_json=module_dict, course_id=course_id
            )
            module_list.append(module)
        return module_list

    async def create_lessons_plan_by_module_id(
        self, module_id: uuid.UUID, user_preferences: str
    ) -> list[LessonModel]:
        module = await self.uow.learning_repo.get_module_by_id(module_id)
        if not module:
            raise ValueError(f"Модуль {module_id} не найден")
        if not module.course:
            raise ValueError(f"Модуль {module_id} не имеет курса")

        course_structure_json = CourseStructureWithModulesOut.model_validate(
            module.course
        ).model_dump_json()
        module_structure_json = ModuleStructureWithLessonsOut.model_validate(
            module
        ).model_dump_json()
        lesson_plan = self.agent.generate_lesson_plan(
            course_structure_json=course_structure_json,
            module_structure_json=module_structure_json,
            user_preferences=user_preferences,
        )
        lesson_list = []
        for lesson_dict in lesson_plan:
            lesson = await self.uow.learning_repo.create_lesson_by_json(
                lesson_dict, module_id=module_id
            )
            lesson_list.append(lesson)
        return lesson_list

    async def initiate_user_learning_by_session_id(
        self, user_id: uuid.UUID, session_id: uuid.UUID
    ):
        courses = await self.uow.learning_repo.get_courses_by_session_id(session_id)
        if not courses:
            raise ValueError(f"Курс для сессии {session_id} не найден")

        for course in courses:
            if not course.preference:
                raise ValueError(f"Курс {course.id} не имеет предпочтения")

            await self.uow.learning_repo.update_course(
                data=CourseUpdate(user_id=user_id),
                course_id=course.id,
            )
            await self.uow.audit_repo.update_course_preference(
                data=PreferenceUpdate(user_id=user_id),
                preference_id=course.preference.id,
            )

    async def get_course_by_id(self, course_id: uuid.UUID):
        return await self.uow.learning_repo.get_course_by_id(course_id)

    async def get_module_by_id(self, module_id: uuid.UUID):
        return await self.uow.learning_repo.get_module_by_id(module_id)

    async def get_lesson_by_id(self, lesson_id: uuid.UUID):
        return await self.uow.learning_repo.get_lesson_by_id(lesson_id)

    async def get_first_module_by_course_id(self, course_id: uuid.UUID):
        course = await self.uow.learning_repo.get_course_by_id(course_id)
        if not course:
            raise ValueError(f"Курс {course_id} не найден")
        return min(course.modules, key=lambda m: m.position)

    async def get_first_lesson_by_module_id(self, module_id: uuid.UUID):
        module = await self.uow.learning_repo.get_module_by_id(module_id)
        if not module:
            raise ValueError(f"Модуль {module_id} не найден")
        return min(module.lessons, key=lambda l: l.position)

    async def generate_and_save_lesson_content_plan(
        self, lesson_id: uuid.UUID, user_preferences: str = ""
    ) -> list[ContentModel]:
        lesson: LessonModel = await self.uow.learning_repo.get_lesson_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Урок {lesson_id} не найден")

        content_plan = CoursePlanAgent().generate_lesson_content_plan(
            lesson_structure_json=LessonStructureOut.model_validate(
                lesson
            ).model_dump_json(),
            module_structure_json=ModuleStructureWithLessonsOut.model_validate(
                lesson.module
            ).model_dump_json(),
            course_structure_json=CourseStructureWithModulesOut.model_validate(
                lesson.module.course
            ).model_dump_json(),
            user_preferences=user_preferences,
        )
        if not isinstance(content_plan, list):
            raise ValueError(
                f"Генерация вернула не список блоков. Ответ: {content_plan}"
            )

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
                outline=content_obj.outline,
            )
            self.uow.session.add(db_content)
            content_list.append(db_content)

        await self.uow.session.commit()
        for db_content in content_list:
            await self.uow.session.refresh(db_content)
        return content_list
