from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    model_config = ConfigDict(from_attributes=True)
