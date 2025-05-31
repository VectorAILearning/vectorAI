import uuid
from agents.plan_agent import CoursePlanAgent
from models import CourseModel, PreferenceModel
from schemas import PreferenceUpdate, CourseUpdate
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
