import uuid
from urllib.parse import urlencode

from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from models import UserModel
from schemas import UserBase
from schemas.auth import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    RefreshTokenRequest,
    RegistrationResponse,
    ResetPasswordRequest,
    Token,
    UserRegister,
)
from services.auth.service import AuthService
from services.learning_service.service import LearningService
from services.session_service.service import SessionService
from utils.auth_utils import is_user
from utils.uow import UnitOfWork, get_uow

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), uow: UnitOfWork = Depends(get_uow)
):
    """
    Авторизация пользователя.
    """
    try:
        service = AuthService(uow)
        user = await service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Неверный email или пароль")
        access_token = service.create_access_token(data={"sub": user.email})
        refresh_token = await service.create_refresh_token(user_id=user.id)
        if not refresh_token:
            raise HTTPException(
                status_code=500, detail="Не удалось создать refresh_token"
            )
        return Token(refresh_token=refresh_token.token, access_token=access_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера",
        )


@auth_router.post("/register", response_model=RegistrationResponse)
async def register(
    request: Request,
    user_data: UserRegister,
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Регистрация пользователя. На указанную почту отправляется письмо для подтверждения.
    """
    try:
        auth_service = AuthService(uow)
        user = await auth_service.register_user(user_data.username, user_data.password)

        if not user:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")

        ip = request.client.host if request.client else "unknown"
        device = request.headers.get("user-agent", "unknown")
        sid = await SessionService(uow).get_session_id_by_ip_user_agent(ip, device)
        if sid:
            await LearningService(uow).initiate_user_learning_by_session_id(
                user.id, uuid.UUID(sid)
            )

        return RegistrationResponse(
            result=f"На вашу почту {user_data.username} "
            f"отправлено письмо для подтверждения учетной записи"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера",
        )


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: RefreshTokenRequest, uow: UnitOfWork = Depends(get_uow)
):
    """
    Обновление access_token с помощью refresh_token.
    """
    try:
        service = AuthService(uow)
        new_tokens = await service.refresh_access_token(token_request.refresh_token)
        return new_tokens
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@auth_router.post("/forgot-password", response_model=RegistrationResponse)
async def forgot_password(
    request_password: ForgotPasswordRequest, uow: UnitOfWork = Depends(get_uow)
):
    """
    Отправка письма со ссылкой для сброса пароля.
    """
    try:
        auth_service = AuthService(uow)
        await auth_service.forgot_password(request_password.username)
        return RegistrationResponse(
            result=f"На вашу почту {request_password.username} отправлено письмо для сброса пароля."
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера",
        )


@auth_router.post("/reset-password", response_model=RegistrationResponse)
async def reset_password(
    request: ResetPasswordRequest, uow: UnitOfWork = Depends(get_uow)
):
    """
    Сброс и установка нового пароля по токену из письма.
    """
    try:
        auth_service = AuthService(uow)
        await auth_service.reset_password(request.token, request.new_password)
        return RegistrationResponse(result="Пароль успешно обновлен!")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@auth_router.post("/google-callback", response_model=Token)
async def auth_via_google(code: GoogleLoginRequest, uow: UnitOfWork = Depends(get_uow)):
    """
    Аутентификация через Google.
    Принимает `code`, возвращает JWT-токены.
    """
    try:
        service = AuthService(uow)
        user = await service.login_with_google(code.code)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось аутентифицировать пользователя через Google",
            )
        access_token = service.create_access_token(data={"sub": user.email})
        refresh_token = await service.create_refresh_token(user_id=user.id)
        return Token(refresh_token=refresh_token.token, access_token=access_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера при аутентификации через Google",
        )


@auth_router.get("/me", response_model=UserBase)
async def me(current_user: UserModel = is_user):
    """
    Получение информации о текущем (аутентифицированном) пользователе.
    """
    return current_user


@auth_router.get("/verify-email", response_model=RegistrationResponse)
async def verify_email(token: str, uow: UnitOfWork = Depends(get_uow)):
    """
    Подтверждение email по токену из письма.
    """
    try:
        auth_service = AuthService(uow)
        await auth_service.verify_user_email(token)
        return RegistrationResponse(result="Email успешно подтвержден!")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@auth_router.get("/google")
async def google_auth():
    """
    Редиректит на страницу авторизации через Google.
    """
    query_params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(query_params)}"
    )
    return RedirectResponse(url=google_auth_url)
