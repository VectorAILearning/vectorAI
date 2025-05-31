import uuid
from uuid import UUID

from pydantic import BaseModel
from typing import List


class AuditRequest(BaseModel):
    client_prompt: str


class AuditResponse(BaseModel):
    user_preference: dict


class ResetChatRequest(BaseModel):
    session_id: UUID


class LessonIn(BaseModel):
    title: str
    description: str = ""
    estimated_time_hours: float = 3


class ModuleIn(BaseModel):
    title: str
    description: str = ""
    estimated_time_hours: float = 15
    lessons: List[LessonIn] = []


class CourseIn(BaseModel):
    course_title: str
    course_description: str = ""
    estimated_time_hours: float = 60
    modules: List[ModuleIn] = []


class PreferenceUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    summary: str | None = None
