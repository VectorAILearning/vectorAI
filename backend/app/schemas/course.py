from pydantic import BaseModel, Field
from typing import Optional, List
import uuid


class LessonIn(BaseModel):
    title: str = Field(default=None, max_length=255)
    description: str = Field(default=None, max_length=255)
    estimated_time_hours: float = 3


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
