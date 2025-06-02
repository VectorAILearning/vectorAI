import uuid
from enum import Enum
from sqlalchemy import Integer, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

class ContentType(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    DIALOG = "dialog"
    OPEN_ANSWER = "open_answer"
    REFLECTION = "reflection"
    TEST = "test"

class ContentModel(Base):
    __tablename__ = "contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False
    )
    type: Mapped[ContentType] = mapped_column(SAEnum(ContentType, name="content_type_enum", create_constraint=True), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    lesson: Mapped["LessonModel"] = relationship(back_populates="contents") 