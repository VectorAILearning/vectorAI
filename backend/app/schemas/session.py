from pydantic import BaseModel
from typing import Optional
import uuid


class SessionCreate(BaseModel):
    ip: Optional[str]
    user_agent: Optional[str]


class SessionUpdate(BaseModel):
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
