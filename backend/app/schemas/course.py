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
    outline: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}


class LessonIn(BaseModel):
    title: str = Field(default="", max_length=255)
    description: str = Field(default="", max_length=1000)
    goal: str = Field(default="", max_length=1000)
    estimated_time_hours: float = 3
    position: int


class ModuleIn(BaseModel):
    title: str = Field(default="", max_length=255)
    description: str = Field(default="", max_length=1000)
    goal: str = Field(default="", max_length=1000)
    estimated_time_hours: float = 15
    lessons: List[LessonIn] = []
    position: int


class CourseIn(BaseModel):
    title: str = Field(default="", max_length=255)
    goal: str = Field(default="", max_length=1000)
    description: str = Field(default="", max_length=1000)
    estimated_time_hours: float = 60
    modules: List[ModuleIn] = []


class CourseUpdate(BaseModel):
    title: str | None = Field(default="", max_length=255)
    description: str | None = Field(default="", max_length=1000)
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
    contents: list[ContentOut] = []
    position: int

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}


class ModuleOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    goal: Optional[str] = None
    estimated_time_hours: float
    is_completed: bool
    lessons: list[LessonOut] = []
    position: int

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}


class CourseOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    goal: Optional[str] = None
    estimated_time_hours: float
    is_completed: bool
    modules: list[ModuleOut] = []

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}


class ContentStructureOut(BaseModel):
    type: str
    description: str
    goal: str

    class Config:
        from_attributes = True


class LessonStructureOut(BaseModel):
    title: str
    description: str
    goal: str

    class Config:
        from_attributes = True


class ModuleStructureOut(BaseModel):
    title: str
    goal: str

    class Config:
        from_attributes = True


class CourseStructureOut(BaseModel):
    title: str
    goal: str

    class Config:
        from_attributes = True


class ModuleStructureWithLessonsOut(ModuleStructureOut):
    lessons: list[LessonStructureOut]

    class Config:
        from_attributes = True


class CourseStructureWithModulesOut(CourseStructureOut):
    modules: list[ModuleStructureOut]

    class Config:
        from_attributes = True


class LessonStructureWithContentsOut(LessonStructureOut):
    contents: list[ContentStructureOut]

    class Config:
        from_attributes = True
