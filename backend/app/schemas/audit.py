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


class PreferenceOut(BaseModel):
    id: uuid.UUID | None = None
    summary: str
    course_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}
