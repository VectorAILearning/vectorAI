import uuid

from core.database import Base
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourseModel(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    goal: Mapped[str] = mapped_column(String(1000), nullable=True)
    
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="courses")
    modules: Mapped[list["ModuleModel"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    preference: Mapped["PreferenceModel"] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    session = relationship("SessionModel", back_populates="courses")


class ModuleModel(Base):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    goal: Mapped[str] = mapped_column(String(1000), nullable=True)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    course: Mapped["CourseModel"] = relationship(back_populates="modules")
    lessons: Mapped[list["LessonModel"]] = relationship(
        back_populates="module", cascade="all, delete-orphan", lazy="selectin"
    )


class LessonModel(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[str] = mapped_column(String(1000), nullable=True)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    module: Mapped["ModuleModel"] = relationship(back_populates="lessons")
    contents: Mapped[list["ContentModel"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan", lazy="selectin"
    )
