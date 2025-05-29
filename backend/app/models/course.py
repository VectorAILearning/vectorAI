from core.database import Base
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourseModel(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    modules: Mapped[list["ModuleModel"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )
    preferences: Mapped[list["PreferenceModel"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", lazy="selectin"
    )


class ModuleModel(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    course: Mapped["CourseModel"] = relationship(back_populates="modules")
    lessons: Mapped[list["LessonModel"]] = relationship(
        back_populates="module", cascade="all, delete-orphan", lazy="selectin"
    )


class LessonModel(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_time_hours: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    module: Mapped["ModuleModel"] = relationship(back_populates="lessons")


class PreferenceModel(Base):
    __tablename__ = "preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    profile_summary: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="preferences")
    course: Mapped["CourseModel"] = relationship(
        "CourseModel", back_populates="preferences"
    )
