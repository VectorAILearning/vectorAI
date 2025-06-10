import uuid
from enum import Enum

from core.database import Base
from sqlalchemy import JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ContentType(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    DIALOG = "dialog"
    PRACTICE = "practice"
    EXAMPLES = "examples"
    MISTAKES = "mistakes"
    REFLECTION = "reflection"
    TEST = "test"
    CODE = "code"


class ContentModel(Base):
    __tablename__ = "contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False
    )
    type: Mapped[ContentType] = mapped_column(
        SAEnum(ContentType, name="content_type_enum", create_constraint=True),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    goal: Mapped[str] = mapped_column(String(1000), nullable=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    outline: Mapped[str] = mapped_column(String(1000), nullable=True)

    lesson: Mapped["LessonModel"] = relationship(back_populates="contents")
