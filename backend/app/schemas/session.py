import uuid
from typing import Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    ip: Optional[str]
    user_agent: Optional[str]


class SessionUpdate(BaseModel):
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[uuid.UUID] = None


class SessionInfoResponse(BaseModel):
    session_id: str
    session: dict
    reset_count: int
    messages: list
    status: str
    generated_courses: Optional[list[dict]] = None
