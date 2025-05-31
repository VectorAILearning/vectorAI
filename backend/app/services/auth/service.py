from datetime import datetime, timedelta

import jwt
from core.config import settings
from models import UserModel
from passlib.context import CryptContext
from pydantic import EmailStr
from utils.uow import UnitOfWork

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now() + (
            expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    async def authenticate_user(self, username: EmailStr, password: str):
        user = await self.uow.auth_repo.get_by_email(username)
        if not user or not self.verify_password(password, user.password):
            return None
        return user

    async def register_user(self, email: EmailStr, password: str):
        existing = await self.uow.auth_repo.get_by_email(email)
        if existing:
            return None
        hashed_password = pwd_context.hash(password)
        user = UserModel(email=email, password=hashed_password, username=email)
        self.uow.session.add(user)
        await self.uow.commit()
        return user
