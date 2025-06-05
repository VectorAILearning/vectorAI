from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from models.task import TaskStatusEnum, TaskTypeEnum
from pydantic import BaseModel


class TaskIn(BaseModel):
    id: UUID = None
    parent_id: Optional[UUID] = None
    task_type: TaskTypeEnum
    params: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: UUID
    parent_id: Optional[UUID] = None
    task_type: TaskTypeEnum
    params: Optional[Dict[str, Any]] = None
    status: TaskStatusEnum
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True
