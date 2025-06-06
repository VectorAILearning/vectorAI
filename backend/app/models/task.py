import enum
from uuid import uuid4

from core.database import Base
from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TaskStatusEnum(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    success = "success"
    failed = "failed"


class TaskTypeEnum(enum.Enum):
    generate_course = "generate_course"
    generate_user_summary = "generate_user_summary"
    generate_course_plan = "generate_course_plan"
    generate_module_plan = "generate_module_plan"
    generate_lesson_plan = "generate_lesson_plan"
    generate_module = "generate_module"
    generate_lesson = "generate_lesson"
    generate_content = "generate_content"


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    parent_id = Column(PGUUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    task_type = Column(SAEnum(TaskTypeEnum), nullable=False)
    params = Column(JSON, nullable=True)
    status = Column(
        SAEnum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.pending
    )
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    parent = relationship("TaskModel", remote_side=[id], backref="subtasks")
