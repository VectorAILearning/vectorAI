import uuid
from typing import Any, List

from pydantic import BaseModel, Field


class ContentOut(BaseModel):
    id: uuid.UUID
    type: str
    description: str | None = None
    content: dict[str, Any]
    position: int

    class Config:
        from_attributes = True


class ContentIn(BaseModel):
    type: str
    description: str | None = None
    position: int = 0


class LessonIn(BaseModel):
    title: str = Field(default=None, max_length=255)
    description: str = Field(default=None, max_length=255)
    estimated_time_hours: float = 3
    contents: List["ContentIn"] = []


class ModuleIn(BaseModel):
    title: str = Field(default=None, max_length=255)
    description: str = Field(default=None, max_length=255)
    estimated_time_hours: float = 15
    lessons: List[LessonIn] = []


class CourseIn(BaseModel):
    course_title: str = Field(default=None, max_length=255)
    course_description: str = Field(default=None, max_length=255)
    estimated_time_hours: float = 60
    modules: List[ModuleIn] = []


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    estimated_time_hours: float | None = None
    is_completed: bool | None = None
    user_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None


class LessonOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    estimated_time_hours: float
    is_completed: bool
    contents: list[ContentOut] = []

    class Config:
        from_attributes = True


class ModuleOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    estimated_time_hours: float
    is_completed: bool
    lessons: list[LessonOut] = []

    class Config:
        from_attributes = True


class CourseOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    estimated_time_hours: float
    is_completed: bool
    modules: list[ModuleOut] = []

    class Config:
        from_attributes = True
