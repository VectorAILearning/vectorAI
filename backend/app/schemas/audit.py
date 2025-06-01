import uuid

from pydantic import BaseModel


class AuditRequest(BaseModel):
    client_prompt: str


class AuditResponse(BaseModel):
    user_preference: dict


class PreferenceUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    summary: str | None = None
