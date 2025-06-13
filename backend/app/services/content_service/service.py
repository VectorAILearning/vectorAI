import json

from agents.content_agent.agent import ContentPlanAgent
from models import ContentModel
from schemas.course import (
    CourseStructureOut,
    LessonOut,
    LessonStructureWithContentsOut,
    ModuleStructureOut,
)
from utils.uow import UnitOfWork


class ContentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.agent = ContentPlanAgent()

    async def generate_content_by_block(self, content_obj: ContentModel):
        lesson = content_obj.lesson
        course = lesson.module.course
        course_context = CourseStructureOut.model_validate(course).model_dump_json()
        module_context = ModuleStructureOut.model_validate(
            lesson.module
        ).model_dump_json()
        lesson_context = LessonStructureWithContentsOut.model_validate(
            lesson
        ).model_dump_json()
        previous_outlines = "->".join([content.outline for content in lesson.contents])
        content = self.agent.generate_content(
            type_=content_obj.type,
            description=content_obj.description,
            goal=content_obj.goal,
            outline=content_obj.outline,
            course_context=course_context,
            lesson_context=lesson_context,
            module_context=module_context,
            previous_outlines=previous_outlines,
        )
        content_obj.content = content
        await self.uow.session.commit()
        await self.uow.session.refresh(content_obj)
        return content_obj
