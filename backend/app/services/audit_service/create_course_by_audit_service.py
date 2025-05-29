from core.database import db_helper
from models import CourseModel, LessonModel, ModuleModel, UserModel
from sqlalchemy import select


async def create_course_from_json(course_json: dict, username: str = "test"):
    async with db_helper.session_factory() as session:
        # TODO: Сделать создание пользователя до создания курса
        # user_stmt = await session.execute(
        #     select(UserModel).where(UserModel.username == username)
        # )
        # user = user_stmt.scalar_one_or_none()
        # if not user:
        #     user = UserModel(username=username)
        #     session.add(user)
        #     await session.commit()
        #     await session.refresh(user)

        course = CourseModel(
            title=course_json.get("course_title", "Курс без названия"),
            description=course_json.get("course_description", ""),
            estimated_time_hours=course_json.get("estimated_time_hours"),
        )
        session.add(course)
        await session.commit()
        await session.refresh(course)

        modules_json = course_json.get("modules", [])
        for module_json in modules_json:
            module = ModuleModel(
                course_id=course.id,
                title=module_json.get("title", "Модуль без названия"),
                description=module_json.get("description", ""),
                estimated_time_hours=module_json.get("estimated_time_hours"),
            )

            session.add(module)
            await session.commit()
            await session.refresh(module)

            for lesson_json in module_json.get("lessons", []):
                lesson = LessonModel(
                    module_id=module.id,
                    title=lesson_json.get("title", "Урок без названия"),
                    description=lesson_json.get("description", ""),
                    estimated_time_hours=lesson_json.get("estimated_time_hours"),
                )
                session.add(lesson)
            await session.commit()

        result = {
            "title": course.title,
            "id": course.id,
        }
        return result
