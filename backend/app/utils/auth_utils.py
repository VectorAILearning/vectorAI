import logging
from typing import List

import jwt
from core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import UserModel, UserRole
from schemas.user import UserBase
from services.auth.service import AuthService
from starlette import status
from utils.uow import UnitOfWork, get_uow

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")
log = logging.getLogger(__name__)


def decode_access_token(token: str) -> dict | None:
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
        detail="Вы не авторизованы",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        log.info(f"payload: {payload}")
        if not email:
            raise credentials_exception
    except jwt.PyJWTError as e:
        log.exception(f"Error in get_current_user: {e}")
        raise credentials_exception

    service = AuthService(uow)
    user = await service.uow.auth_repo.get_by_email(email)
    if not user:
        raise credentials_exception
    return UserBase.model_validate(user)


def require_roles(required_roles: List[UserRole]):
    def role_checker(current_user: UserModel = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"У вас нет прав для выполнения этого действия. Требуется одна из ролей: {', '.join(r.value for r in required_roles)}",
            )
        return current_user

    return role_checker


is_admin = Depends(require_roles([UserRole.ADMIN]))
is_user = Depends(require_roles([UserRole.USER, UserRole.ADMIN]))
