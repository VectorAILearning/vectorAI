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
    """Типы задач
    Args:
        generate_course(str): генерация курса полностью (название, описание, цель, модули, уроки, блоки контента)
        generate_lesson(str): генерация урока полностью (блоки контента в уроке, контент в блоках)
        generate_user_summary(str): генерация предпочтения пользователя
        generate_course_base(str): генерация курса (название, описание, цель)
        generate_course_plan(str): генерация плана курса (модулей в курсе)
        generate_module_plan(str): генерация плана модуля (уроков в модуле)
        generate_lesson_content_plan(str): генерация плана урока (блоки контента в уроке)
        generate_content(str): генерация контента (блоки контента в уроке)
    """

    generate_course = "generate_course"
    generate_lesson = "generate_lesson"
    generate_user_summary = "generate_user_summary"
    generate_course_base = "generate_course_base"
    generate_course_plan = "generate_course_plan"
    generate_module_plan = "generate_module_plan"
    generate_lesson_content_plan = "generate_lesson_content_plan"
    generate_content = "generate_content"


class TaskModel(Base):
    """Модель задачи
    Args:
        id(UUID): id задачи Arq
        parent_id(UUID): id родительской задачи
        task_type(TaskTypeEnum): тип задачи
        params(dict): параметры задачи
        status(TaskStatusEnum): статус задачи
        result(dict): результат задачи (выходные данные)
        error_message(str): сообщение об ошибке
        created_at(datetime): дата создания задачи
        started_at(datetime): дата начала выполнения задачи
        finished_at(datetime): дата окончания выполнения задачи
        session_id(UUID): id сессии
        user_id(UUID): id пользователя
    """

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
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    session = relationship("SessionModel", backref="tasks")
    user = relationship("UserModel", backref="tasks")
    parent = relationship("TaskModel", remote_side=[id], backref="subtasks")
