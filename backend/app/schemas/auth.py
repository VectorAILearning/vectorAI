from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    refresh_token: str
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserRegister(BaseModel):
    username: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegistrationResponse(BaseModel):
    result: str


class ForgotPasswordRequest(BaseModel):
    username: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class GoogleLoginRequest(BaseModel):
    code: str
