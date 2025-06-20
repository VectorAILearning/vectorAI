import logging
import uuid
from urllib.parse import urlencode

from core.config import settings
from core.database import get_async_session
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
from services.auth.service import get_auth_service
from services.learning_service.service import get_learning_service
from services.session_service.service import get_session_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth_utils import is_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])


log = logging.getLogger(__name__)


@auth_router.post("/login", response_model=Token)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Авторизация пользователя.
    """
    try:
        auth_service = get_auth_service(async_session)
        user = await auth_service.authenticate_user(
            form_data.username, form_data.password
        )
        if not user:
            raise HTTPException(status_code=400, detail="Неверный email или пароль")
        access_token = auth_service.create_access_token(data={"sub": user.email})

        sid = request.cookies.get(settings.SESSION_COOKIE_KEY)

        session_service = get_session_service(async_session)
        if not sid or not await session_service.check_session(sid):
            session_info = await session_service.create_session()
            response.set_cookie(
                key=settings.SESSION_COOKIE_KEY,
                value=session_info["session_id"],
                httponly=True,
                secure=settings.SECURE_COOKIES,
                samesite="lax",
                max_age=settings.SESSION_TTL,
            )
            sid = session_info["session_id"]

        await session_service.attach_user(sid, str(user.id))
        learning_service = get_learning_service(async_session)
        await learning_service.init_user_courses_by_session_id(user.id, uuid.UUID(sid))
        refresh_token = await auth_service.create_refresh_token(user_id=user.id)
        if not refresh_token:
            raise HTTPException(
                status_code=500, detail="Не удалось создать refresh_token"
            )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token.token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        )
        return Token(access_token=access_token)
    except HTTPException as e:
        log.exception(f"Error in login: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера",
        )


@auth_router.post("/register", response_model=RegistrationResponse)
async def register(
    user_data: UserRegister,
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Регистрация пользователя. На указанную почту отправляется письмо для подтверждения.
    Курсы пользователя созданные в сессии подвязываются к его аккаунту.
    """
    try:
        auth_service = get_auth_service(async_session)
        await auth_service.register_user(user_data.username, user_data.password)

        return RegistrationResponse(
            result=f"На вашу почту {user_data.username} "
            f"отправлено письмо для подтверждения учетной записи"
        )
    except HTTPException as e:
        log.exception(f"Error in register: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in register: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера",
        )


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    request: Request,
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Обновление access_token с помощью refresh_token.
    """
    try:
        auth_service = get_auth_service(async_session)
        old_refresh_token = request.cookies.get("refresh_token")
        if not old_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token не найден",
            )
        new_tokens = await auth_service.refresh_access_token(old_refresh_token)
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось обновить токен",
            )
        response.set_cookie(
            key="refresh_token",
            value=new_tokens["refresh_token"],
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        )
        return Token(access_token=new_tokens["access_token"])
    except HTTPException as e:
        log.exception(f"Error in refresh: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@auth_router.post("/forgot-password", response_model=RegistrationResponse)
async def forgot_password(
    request_password: ForgotPasswordRequest,
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Отправка письма со ссылкой для сброса пароля.
    """
    try:
        auth_service = get_auth_service(async_session)
        await auth_service.forgot_password(request_password.username)
        return RegistrationResponse(
            result=f"На вашу почту {request_password.username} отправлено письмо для сброса пароля."
        )
    except HTTPException as e:
        log.exception(f"Error in forgot_password: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in forgot_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на стороне сервера",
        )


@auth_router.post("/reset-password", response_model=RegistrationResponse)
async def reset_password(
    request: ResetPasswordRequest,
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Сброс и установка нового пароля по токену из письма.
    """
    try:
        auth_service = get_auth_service(async_session)
        await auth_service.reset_password(request.token, request.new_password)
        return RegistrationResponse(result="Пароль успешно обновлен!")
    except HTTPException as e:
        log.exception(f"Error in reset_password: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in reset_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@auth_router.post("/google-callback", response_model=Token)
async def auth_via_google(
    code: GoogleLoginRequest,
    response: Response,
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Аутентификация через Google.
    Принимает `code`, возвращает JWT-токены.
    """
    try:
        auth_service = get_auth_service(async_session)
        user = await auth_service.login_with_google(code.code)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось аутентифицировать пользователя через Google",
            )
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
    except HTTPException as e:
        log.exception(f"Error in auth_via_google: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in auth_via_google: {e}")
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
async def verify_email(
    token: str, async_session: AsyncSession = Depends(get_async_session)
):
    """
    Подтверждение email по токену из письма.
    """
    try:
        auth_service = get_auth_service(async_session)
        await auth_service.verify_user_email(token)
        return RegistrationResponse(result="Email успешно подтвержден!")
    except HTTPException as e:
        log.exception(f"Error in verify_email: {e}")
        raise e
    except Exception as e:
        log.exception(f"Error in verify_email: {e}")
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


@auth_router.post("/logout", response_model=RegistrationResponse)
async def logout(
    response: Response,
):
    """
    Выход пользователя. Удаляет куки refresh_token.
    """
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_KEY,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
    )
    return RegistrationResponse(result="Вы успешно вышли из системы")
