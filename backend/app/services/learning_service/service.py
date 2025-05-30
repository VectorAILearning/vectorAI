from agents.audit_agent import AuditAgent
from agents.plan_agent import CoursePlanAgent
from utils.uow import UnitOfWork


# TODO: Доделать сервис создания обучения
class LearningService:
    def __init__(self, websocket, redis_service, session_id: str, uow: UnitOfWork):
        self.ws = websocket
        self.redis = redis_service
        self.sid = session_id
        self.agent = AuditAgent()
        self.uow = uow

    async def create_course_by_user_preference(self, preference: str):
        course_plan = CoursePlanAgent().generate_course(preference)
        course = self.uow.audit_repo.create_course_by_json(course_plan)
        return {
            "id": course.id,
            "title": course.title,
        }
