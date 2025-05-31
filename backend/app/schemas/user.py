import uuid

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    refresh_token: str
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserRegister(BaseModel):
    username: EmailStr
    password: str
    session_id: uuid.UUID | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
