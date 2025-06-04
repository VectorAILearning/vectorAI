import uuid
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ContentOut(BaseModel):
    id: uuid.UUID | None = None
    type: str
    content: dict[str, Any] | None = None
    position: int
    description: Optional[str] = None
    goal: Optional[str] = None

    class Config:
        from_attributes = True


class LessonIn(BaseModel):
    title: str = Field(default=None, max_length=255)
    description: str = Field(default=None, max_length=1000)
    goal: str = Field(default=None, max_length=1000)
    estimated_time_hours: float = 3
    position: int
    status: str = "draft"


class ModuleIn(BaseModel):
    title: str = Field(default=None, max_length=255)
    description: str = Field(default=None, max_length=1000)
    goal: str = Field(default=None, max_length=1000)
    estimated_time_hours: float = 15
    lessons: List[LessonIn] = []
    position: int
    status: str = "draft"


class CourseIn(BaseModel):
    title: str = Field(default=None, max_length=255)
    goal: str = Field(default=None, max_length=1000)
    description: str = Field(default=None, max_length=255)
    estimated_time_hours: float = 60
    modules: List[ModuleIn] = []
    status: str = "draft"


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
    goal: Optional[str] = None
    estimated_time_hours: float
    is_completed: bool
    status: str = "draft"
    contents: list[ContentOut] = []
    position: int

    class Config:
        from_attributes = True


class ModuleOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    goal: Optional[str] = None
    estimated_time_hours: float
    is_completed: bool
    status: str = "draft"
    lessons: list[LessonOut] = []
    position: int

    class Config:
        from_attributes = True


class CourseOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    goal: Optional[str] = None
    estimated_time_hours: float
    is_completed: bool
    status: str = "draft"
    modules: list[ModuleOut] = []

    class Config:
        from_attributes = True
