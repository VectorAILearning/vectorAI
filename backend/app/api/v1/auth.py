import logging
from urllib.parse import urlencode

from core.config import settings
from core.constants import AuthErrorMessages
from core.dependencies import get_auth_service
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from models import UserModel
from schemas import UserBase
from schemas.auth import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    RegistrationResponse,
    ResetPasswordRequest,
    Token,
    UserRegister,
)
from services.auth.service import AuthService
from utils.auth_utils import is_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])

log = logging.getLogger(__name__)


@auth_router.post("/login", response_model=Token)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Авторизация пользователя.

    Args:
        request: HTTP запрос
        response: HTTP ответ
        form_data: Форма с данными логина
        auth_service: Сервис аутентификации (из DI контейнера)

    Returns:
        Token: JWT токены для доступа
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(user_id=user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token.token,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=access_token)


@auth_router.post("/register", response_model=RegistrationResponse)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Регистрация пользователя. На указанную почту отправляется письмо для подтверждения.
    """
    await auth_service.register_user(user_data.username, user_data.password)

    return RegistrationResponse(
        result=AuthErrorMessages.EMAIL_VERIFICATION_SENT.format(user_data.username)
    )


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Обновление access_token с помощью refresh_token.
    """
    old_refresh_token = request.cookies.get("refresh_token")
    if not old_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessages.REFRESH_TOKEN_NOT_FOUND,
        )

    new_tokens = await auth_service.refresh_access_token(old_refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_tokens["refresh_token"],
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=new_tokens["access_token"])


@auth_router.post("/forgot-password", response_model=RegistrationResponse)
async def forgot_password(
    request_password: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Отправка письма со ссылкой для сброса пароля.
    """
    await auth_service.forgot_password(request_password.username)
    return RegistrationResponse(
        result=AuthErrorMessages.PASSWORD_RESET_SENT.format(request_password.username)
    )


@auth_router.post("/reset-password", response_model=RegistrationResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Сброс и установка нового пароля по токену из письма.
    """
    await auth_service.reset_password(request.token, request.new_password)
    return RegistrationResponse(result=AuthErrorMessages.PASSWORD_UPDATED)


@auth_router.post("/google-callback", response_model=Token)
async def auth_via_google(
    code: GoogleLoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Аутентификация через Google.
    """
    user = await auth_service.login_with_google(code.code)

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(user_id=user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token.token,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=access_token)


@auth_router.get("/me", response_model=UserBase)
async def me(current_user: UserModel = is_user):
    """
    Получение информации о текущем пользователе.
    """
    return current_user


@auth_router.get("/verify-email", response_model=RegistrationResponse)
async def verify_email(
    token: str, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Подтверждение email по токену из письма.
    """
    await auth_service.verify_user_email(token)
    return RegistrationResponse(result="Email успешно подтвержден!")


@auth_router.get("/google")
async def google_auth():
    """
    Перенаправление на Google OAuth.
    """
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{google_auth_url}?{urlencode(params)}"
    return RedirectResponse(url=url)


@auth_router.post("/logout", response_model=RegistrationResponse)
async def logout(
    response: Response,
):
    """
    Выход из системы - удаление refresh_token cookie.
    """
    response.delete_cookie(key="refresh_token")
    return RegistrationResponse(result=AuthErrorMessages.LOGOUT_SUCCESS)
