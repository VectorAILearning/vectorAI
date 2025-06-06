import json

from agents.content_agent.agent import ContentPlanAgent
from models import ContentModel
from schemas.course import CourseOut, LessonOut
from utils.uow import UnitOfWork


class ContentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.agent = ContentPlanAgent()

    async def generate_content_by_block(self, content_obj: ContentModel):
        lesson = content_obj.lesson
        course = lesson.module.course
        course_context = json.dumps(
            CourseOut.model_validate(course).model_dump(),
            ensure_ascii=False,
            default=str,
        )
        lesson_context = json.dumps(
            LessonOut.model_validate(lesson).model_dump(),
            ensure_ascii=False,
            default=str,
        )
        content = self.agent.generate_content(
            type_=content_obj.type,
            description=content_obj.description,
            goal=content_obj.goal,
            course_context=course_context,
            lesson_context=lesson_context,
        )
        content_obj.content = content
        await self.uow.session.commit()
        await self.uow.session.refresh(content_obj)
        return content_obj
