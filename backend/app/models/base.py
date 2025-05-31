import uuid
from datetime import datetime

from core.database import Base
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import Boolean, DateTime


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
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


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
        UUID(as_uuid=True), ForeignKey("courses.id"), unique=True, nullable=True
    )
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="preferences")
    course: Mapped["CourseModel"] = relationship(
        "CourseModel", back_populates="preference"
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


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["UserModel"] = relationship(
        back_populates="refresh_tokens", lazy="selectin"
    )
