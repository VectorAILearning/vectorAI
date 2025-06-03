import uuid

from agents.content_agent.agent import ContentAgent
from agents.lesson_agent.agent import LessonPlanAgent
from agents.plan_agent.agent import CoursePlanAgent
from models import ContentModel, CourseModel, PreferenceModel
from models.content import ContentType
from schemas import CourseUpdate, PreferenceUpdate
from utils.uow import UnitOfWork


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

    async def generate_and_save_lesson_plan(self, lesson, user_preferences: str = ""):
        agent = LessonPlanAgent()
        plan = agent.generate_plan(
            lesson_description=f"{lesson.title}. {lesson.description}",
            user_preferences=user_preferences,
        )
        if not isinstance(plan, list):
            raise ValueError(f"Генерация вернула не список блоков. Ответ: {plan}")
        db = self.uow.session
        for block in plan:
            if (
                not isinstance(block, dict)
                or "type" not in block
                or "description" not in block
                or "position" not in block
            ):
                raise ValueError(f"Некорректный формат блока: {block}")
            db_content = ContentModel(
                lesson_id=lesson.id,
                type=ContentType(block["type"]),
                description=block["description"],
                content={},
                position=block["position"],
            )
            db.add(db_content)
        await db.commit()
        return plan

    async def generate_and_save_lesson_content(
        self, lesson, user_preferences: str = ""
    ):
        agent = ContentAgent()
        content = agent.generate_content(
            lesson_description=f"{lesson.title}. {lesson.description}",
            user_preferences=user_preferences,
        )
        if not isinstance(content, list):
            raise ValueError(f"Генерация вернула не список блоков. Ответ: {content}")
        db = self.uow.session
        for block in content:
            if (
                not isinstance(block, dict)
                or "type" not in block
                or "content" not in block
                or "position" not in block
            ):
                raise ValueError(f"Некорректный формат блока: {block}")
            db_content = ContentModel(
                lesson_id=lesson.id,
                type=ContentType(block["type"]),
                description=block.get("description"),
                content=block["content"],
                position=block["position"],
            )
            db.add(db_content)
        await db.commit()
        return content
