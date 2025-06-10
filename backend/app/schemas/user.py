from uuid import UUID

from models import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)
