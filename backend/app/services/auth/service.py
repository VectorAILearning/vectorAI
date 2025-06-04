import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Self

import bcrypt
import jwt
from core.config import settings
from fastapi import HTTPException, status
from models import RefreshTokenModel, UserModel
from pydantic import EmailStr
from schemas import Token
from utils.email_sender import send_verification_email
from utils.uow import UnitOfWork


class AuthService:
    def __init__(self: Self, uow: UnitOfWork) -> None:
        self.uow = uow

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return bcrypt.checkpw(
            bytes(plain_password, encoding="utf-8"),
            bytes(hashed_password, encoding="utf-8"),
        )

    @staticmethod
    def get_password_hash(password):
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        )
        return hashed.decode("utf-8")

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire.timestamp()})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    async def authenticate_user(
        self, username: EmailStr, password: str
    ) -> UserModel | None:
        user = await self.uow.auth_repo.get_by_email(username)
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Email не подтвержден"
            )
        return user

    async def register_user(self, email: EmailStr, password: str) -> UserModel | None:
        existing_user = await self.uow.auth_repo.get_by_email(email)
        if existing_user:
            return None
        hashed_password = self.get_password_hash(password)
        user = UserModel(email=email, password=hashed_password, username=email)
        self.uow.session.add(user)
        await self.uow.session.flush()
        await self.uow.session.refresh(user)
        verification_token = self.create_email_verification_token(user.email)
        await send_verification_email(email, verification_token)
        return user

    @staticmethod
    def _generate_refresh_token_string(length: int = 64) -> str:
        return secrets.token_urlsafe(length)

    async def create_refresh_token(
        self,
        user_id: uuid.UUID,
    ) -> RefreshTokenModel:
        await self.uow.refresh_token_repo.revoke_all_for_user(user_id)

        token_str = self._generate_refresh_token_string()
        expires_delta = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.now(timezone.utc) + expires_delta
        refresh_token_db = RefreshTokenModel(
            user_id=user_id, token=token_str, expires_at=expires_at
        )
        self.uow.session.add(refresh_token_db)
        await self.uow.session.flush()
        await self.uow.session.refresh(refresh_token_db)
        return refresh_token_db

    @staticmethod
    def create_email_verification_token(email: EmailStr) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "sub": email,
            "exp": expire.timestamp(),
            "type": "email_verification",
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    async def verify_user_email(self, token: str) -> bool:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный тип токена",
                )
            email: EmailStr = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Токен не содержит email",
                )

            user = await self.uow.auth_repo.get_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден",
                )
            if user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email уже подтвержден",
                )

            user.is_verified = True
            self.uow.session.add(user)
            await self.uow.session.flush()
            return True
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Токен просрочен"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный токен"
            )

    async def refresh_access_token(self, refresh_token_str: str) -> Token:
        rt_from_db = await self.uow.refresh_token_repo.get_by_token(refresh_token_str)
        if not rt_from_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token не найден",
            )
        if rt_from_db.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token отозван"
            )
        if rt_from_db.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token истёк"
            )

        user = rt_from_db.user
        if not user:
            _user_check = await self.uow.auth_repo.get_by_id(ident=rt_from_db.user_id)
            if not _user_check:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пользователь не найден",
                )
            user = _user_check
        new_access_token = self.create_access_token(data={"sub": user.email})

        await self.uow.refresh_token_repo.revoke(rt_from_db.id)
        new_refresh_token_db = await self.create_refresh_token(user_id=user.id)
        return Token(
            access_token=new_access_token, refresh_token=new_refresh_token_db.token
        )
