import uuid
from core.database import Base
from sqlalchemy import Boolean, Float, ForeignKey, String, Text
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

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="courses")
    modules: Mapped[list["ModuleModel"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    preferences: Mapped[list["PreferenceModel"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
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

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
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

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    module: Mapped["ModuleModel"] = relationship(back_populates="lessons")
