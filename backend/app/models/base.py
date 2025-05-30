import uuid

from core.database import Base
from sqlalchemy import String
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


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ip: Mapped[str] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)

    # courses: Mapped[list["CourseModel"]] = relationship(
    #     cascade="all, delete-orphan", lazy="selectin"
    # )
    # preferences: Mapped[list["PreferenceModel"]] = relationship(
    #     cascade="all, delete-orphan", lazy="selectin"
    # )
