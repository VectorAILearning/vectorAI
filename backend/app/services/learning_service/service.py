from agents.plan_agent import CoursePlanAgent
from core.database import db_helper
from models import CourseModel, PreferenceModel
from schemas import PreferenceUpdate
from utils.uow import UnitOfWork


class LearningService:
    def __init__(self, uow: UnitOfWork, agent: CoursePlanAgent):
        self.agent = agent
        self.uow = uow

    async def create_course_by_user_preference(
        self, preference: PreferenceModel, sid: str
    ) -> CourseModel:
        course_plan = self.agent.generate_course(preference.summary)
        course = await self.uow.learning_repo.create_course_by_json(
            course_plan, session_id=sid
        )
        await self.uow.audit_repo.update_user_preference(
            preference.id, PreferenceUpdate(course_id=course.id)
        )
        return course


async def get_learning_service() -> LearningService:
    agent = CoursePlanAgent()
    async with db_helper.session_factory() as session:
        uow = UnitOfWork(session=session)
        return LearningService(uow=uow, agent=agent)
