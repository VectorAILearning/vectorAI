import enum
import uuid

from models.task import TaskTypeEnum
from pydantic import BaseModel


class GenerateDeepEnum(str, enum.Enum):
    user_summary = "user_summary"
    course_base = "course_base"
    course_plan = "course_plan"
    module_plan = "module_plan"
    lesson_content_plan = "lesson_content_plan"
    first_lesson_content = "first_lesson_content"
    lesson_content = "lesson_content"


class GenerateTaskContext(BaseModel):
    main_task_id: str
    main_task_type: TaskTypeEnum
    deep: str | None = None
    session_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    params: dict | None = None
