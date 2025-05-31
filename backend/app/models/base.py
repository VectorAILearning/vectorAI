import uuid

from core.database import Base
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False)

    courses: Mapped[list["CourseModel"]] = relationship(back_populates="user")
    preferences: Mapped[list["PreferenceModel"]] = relationship(back_populates="user")


class PreferenceModel(Base):
    __tablename__ = "preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True
    )
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="preferences")
    course: Mapped["CourseModel"] = relationship(
        "CourseModel", back_populates="preferences"
    )
    session = relationship("SessionModel", back_populates="preferences")


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ip: Mapped[str] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)

    courses: Mapped[list["CourseModel"]] = relationship(back_populates="session")
    preferences: Mapped[list["PreferenceModel"]] = relationship(
        back_populates="session"
    )
