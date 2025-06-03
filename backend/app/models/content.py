from __future__ import annotations

import uuid
from enum import Enum

from core.database import Base
from sqlalchemy import JSON, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .course import LessonModel


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
    type: Mapped[ContentType] = mapped_column(
        SAEnum(ContentType, name="content_type_enum", create_constraint=True),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    lesson: Mapped["LessonModel"] = relationship(back_populates="contents")
