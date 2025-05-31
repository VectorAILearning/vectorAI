import uuid
from typing import List
from uuid import UUID

from pydantic import BaseModel


class AuditRequest(BaseModel):
    client_prompt: str


class AuditResponse(BaseModel):
    user_preference: dict


class ResetChatRequest(BaseModel):
    session_id: UUID


class PreferenceUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    summary: str | None = None
