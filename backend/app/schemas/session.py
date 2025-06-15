from typing import Optional

from pydantic import BaseModel


class SessionInfoResponse(BaseModel):
    session_id: str
    session: dict
    reset_count: int
    messages: list
    status: str
    generated_courses: Optional[list[dict]] = None
