import jwt
from core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from schemas.user import UserBase
from services.auth.servise import AuthService
from starlette import status
from utils.uow import UnitOfWork, get_uow

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def decode_access_token(token: str):
    import jwt

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), uow: UnitOfWork = Depends(get_uow)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    service = AuthService(uow)
    user = await service.uow.auth_repo.get_by_email(email)
    if user is None:
        raise credentials_exception
    return UserBase.model_validate(user)
