import uuid
from datetime import datetime
from typing import Any
from uuid import UUID

from models.task import TaskStatusEnum, TaskTypeEnum
from pydantic import BaseModel


class TaskIn(BaseModel):
    id: UUID
    parent_id: UUID | None = None
    task_type: TaskTypeEnum
    params: Any | None = None
    session_id: UUID | None = None
    user_id: UUID | None = None

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}


class TaskPatch(BaseModel):
    status: TaskStatusEnum | None = None
    result: Any | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}


class TaskOut(BaseModel):
    id: UUID
    parent_id: UUID | None = None
    task_type: TaskTypeEnum
    params: Any | None = None
    status: TaskStatusEnum
    result: Any | None = None
    session_id: UUID | None = None
    user_id: UUID | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}
