from sqlalchemy.ext.asyncio import AsyncSession
from schemas import CourseIn
from models import CourseModel, ModuleModel, LessonModel


class LearningRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_course_by_json(self, course_json: dict):
        # TODO: сделать связь session_id + course
        course_in = CourseIn(**course_json)

        course = CourseModel(
            title=course_in.course_title,
            description=course_in.course_description,
            estimated_time_hours=course_in.estimated_time_hours,
            modules=[
                ModuleModel(
                    title=mod.title,
                    description=mod.description,
                    estimated_time_hours=mod.estimated_time_hours,
                    lessons=[
                        LessonModel(
                            title=les.title,
                            description=les.description,
                            estimated_time_hours=les.estimated_time_hours,
                        )
                        for les in mod.lessons
                    ],
                )
                for mod in course_in.modul
            ],
        )
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)

        return course
