import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Self

import bcrypt
import httpx
import jwt
from core.config import settings
from core.constants import AuthErrorMessages
from core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    DuplicateError,
    ExternalServiceError,
    NotFoundError,
    TokenError,
    ValidationError,
)
from models import RefreshTokenModel, UserModel
from pydantic import EmailStr
from schemas import Token
from services.auth.repositories.auth import AuthRepository
from services.auth.repositories.token_refresh import RefreshTokenRepository
from sqlalchemy.ext.asyncio import AsyncSession
from utils.email_sender import send_password_reset_email, send_verification_email


class AuthService:
    def __init__(
        self: Self,
        session: AsyncSession,
        auth_repo: AuthRepository,
        refresh_token_repo: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.auth_repo = auth_repo
        self.refresh_token_repo = refresh_token_repo

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля против хеша"""
        return bcrypt.checkpw(
            bytes(plain_password, encoding="utf-8"),
            bytes(hashed_password, encoding="utf-8"),
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Создание хеша пароля"""
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        )
        return hashed.decode("utf-8")

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Создание JWT access токена"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire.timestamp()})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    async def authenticate_user(self, email: EmailStr, password: str) -> UserModel:
        """
        Аутентификация пользователя по email и паролю.

        Args:
            email: Email пользователя для поиска в БД
            password: Пароль пользователя в открытом виде

        Returns:
            UserModel: Аутентифицированный пользователь

        Raises:
            AuthenticationError: При неверных данных для входа
            AuthorizationError: При неподтвержденном email
            DatabaseError: При ошибке базы данных

        Note:
            Пароль проверяется с использованием bcrypt для безопасности
        """
        # Валидация входных данных
        if not email or not password:
            raise AuthenticationError("Email и пароль обязательны")

        if len(password.strip()) < 3:  # Базовая валидация
            raise AuthenticationError(AuthErrorMessages.INVALID_CREDENTIALS)

        try:
            user = await self.auth_repo.get_by_email(email)
            if not user or not self.verify_password(password, user.password):
                raise AuthenticationError(AuthErrorMessages.INVALID_CREDENTIALS)

            if not user.is_verified:
                raise AuthorizationError(AuthErrorMessages.EMAIL_NOT_VERIFIED)

            return user
        except (AuthenticationError, AuthorizationError):
            # Пропускаем наши кастомные исключения
            raise
        except Exception as e:
            # Оборачиваем другие исключения
            raise DatabaseError(AuthErrorMessages.AUTHENTICATION_FAILED) from e

    async def register_user(self, email: EmailStr, password: str) -> UserModel:
        """
        Регистрация нового пользователя с валидацией данных.

        Args:
            email: Email пользователя (будет использован как username)
            password: Пароль пользователя (минимум 6 символов)

        Returns:
            UserModel: Созданный пользователь (с is_verified=False)

        Raises:
            DuplicateError: Если пользователь с таким email уже существует
            ValidationError: Если данные не прошли валидацию
            DatabaseError: При ошибке сохранения в БД

        Note:
            После регистрации отправляется email с токеном подтверждения
        """
        # Валидация входных данных
        if not email or not password:
            raise ValidationError("Email и пароль обязательны")

        if len(password.strip()) < 6:
            raise ValidationError("Пароль должен содержать минимум 6 символов")

        if len(email.strip()) < 5 or "@" not in email:
            raise ValidationError("Некорректный формат email")

        try:
            # Проверяем существование пользователя
            if await self.auth_repo.email_exists(email):
                raise DuplicateError("User", "email", email)

            # Создаем пользователя
            hashed_password = self.get_password_hash(password)
            username = email.split("@")[0]
            user = UserModel(email=email, password=hashed_password, username=username)

            # Сохраняем в БД
            await self.auth_repo.save(user)
            await self.session.commit()
            await self.session.refresh(user)

            # Отправляем email подтверждения
            verification_token = self.create_email_verification_token(user.email)
            await send_verification_email(email, verification_token)

            return user
        except (DuplicateError, ValidationError):
            # Пропускаем кастомные исключения
            raise
        except Exception as e:
            # Откатываем транзакцию и оборачиваем в DatabaseError
            await self.session.rollback()
            raise DatabaseError(AuthErrorMessages.REGISTRATION_FAILED) from e

    @staticmethod
    def _generate_refresh_token_string(length: int = 64) -> str:
        """Генерация строки refresh токена"""
        return secrets.token_urlsafe(length)

    async def create_refresh_token(self, user_id: uuid.UUID) -> RefreshTokenModel:
        """
        Создание нового refresh токена для пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Созданный refresh токен

        Raises:
            DatabaseError: При ошибке создания токена
        """
        try:
            await self.refresh_token_repo.revoke_all_for_user(user_id)

            token_str = self._generate_refresh_token_string()
            expires_delta = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
            expires_at = datetime.now(timezone.utc) + expires_delta
            refresh_token_db = RefreshTokenModel(
                user_id=user_id, token=token_str, expires_at=expires_at
            )
            self.session.add(refresh_token_db)
            await self.session.commit()
            await self.session.refresh(refresh_token_db)
            return refresh_token_db
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(AuthErrorMessages.REFRESH_TOKEN_CREATION_FAILED) from e

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

    @staticmethod
    def create_password_reset_token(email: EmailStr) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "sub": email,
            "exp": expire.timestamp(),
            "type": "password_reset",
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
                raise AuthenticationError(AuthErrorMessages.INVALID_TOKEN_TYPE)
            email: EmailStr = payload.get("sub")
            if not email:
                raise AuthenticationError(AuthErrorMessages.TOKEN_MISSING_EMAIL)

            user = await self.auth_repo.get_by_email(email)
            if not user:
                raise NotFoundError("User", email)
            if user.is_verified:
                raise AuthenticationError(AuthErrorMessages.EMAIL_ALREADY_VERIFIED)

            user.is_verified = True
            self.session.add(user)
            await self.session.commit()
            return True
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(AuthErrorMessages.TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise AuthenticationError(AuthErrorMessages.INVALID_TOKEN)

    async def refresh_access_token(self, refresh_token_str: str) -> dict[str, str]:
        rt_from_db = await self.refresh_token_repo.get_by_token(refresh_token_str)
        if not rt_from_db:
            raise AuthenticationError(AuthErrorMessages.REFRESH_TOKEN_NOT_FOUND)
        if rt_from_db.revoked:
            raise AuthenticationError(AuthErrorMessages.REFRESH_TOKEN_REVOKED)
        if rt_from_db.expires_at <= datetime.now(timezone.utc):
            raise AuthenticationError(AuthErrorMessages.REFRESH_TOKEN_EXPIRED)

        user = rt_from_db.user
        if not user:
            _user_check = await self.auth_repo.get_by_id(ident=rt_from_db.user_id)
            if not _user_check:
                raise AuthenticationError(AuthErrorMessages.USER_NOT_FOUND)
            user = _user_check
        new_access_token = self.create_access_token(data={"sub": user.email})

        await self.refresh_token_repo.revoke(rt_from_db.id)
        new_refresh_token_db = await self.create_refresh_token(user_id=user.id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token_db.token,
        }

    async def forgot_password(self, email: EmailStr):
        user = await self.auth_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User", email)
        reset_token = self.create_password_reset_token(email)
        await send_password_reset_email(email, reset_token)

    async def reset_password(self, token: str, new_password: str):
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "password_reset":
                raise AuthenticationError(AuthErrorMessages.INVALID_TOKEN_TYPE)
            email: str = payload.get("sub")
            if not email:
                raise AuthenticationError(AuthErrorMessages.TOKEN_MISSING_EMAIL)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(AuthErrorMessages.TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise AuthenticationError(AuthErrorMessages.INVALID_TOKEN)

        user = await self.auth_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User", email)

        user.password = self.get_password_hash(new_password)
        self.session.add(user)
        await self.session.commit()

    async def login_with_google(self, code: str) -> UserModel:
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)

        if token_response.status_code != 200:
            raise ExternalServiceError(
                "Google",
                AuthErrorMessages.GOOGLE_TOKEN_FAILED,
                token_response.status_code,
            )

        token_json = token_response.json()
        access_token = token_json.get("access_token")

        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            user_response = await client.get(user_info_url, headers=headers)

        if user_response.status_code != 200:
            raise ExternalServiceError(
                "Google",
                AuthErrorMessages.GOOGLE_USER_INFO_FAILED,
                user_response.status_code,
            )

        user_info = user_response.json()
        email = user_info.get("email")
        if not email:
            raise ExternalServiceError("Google", AuthErrorMessages.GOOGLE_EMAIL_MISSING)

        user = await self.auth_repo.get_by_email(email)
        if not user:
            # Создаем нового пользователя
            username = email.split("@")[0]
            user = UserModel(
                email=email,
                username=username,
                password=secrets.token_urlsafe(32),  # Случайный пароль
                is_verified=True,  # Google уже верифицировал email
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        return user
