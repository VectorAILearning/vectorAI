from uuid import UUID

from pydantic import BaseModel


class AuditRequest(BaseModel):
    client_prompt: str


class AuditResponse(BaseModel):
    user_preference: dict


class ResetChatRequest(BaseModel):
    session_id: UUID
