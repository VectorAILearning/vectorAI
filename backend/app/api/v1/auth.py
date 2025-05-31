from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import RefreshTokenRequest, Token, UserRegister
from services.auth.service import AuthService
from services.learning_service.service import LearningService
from utils.auth_utils import get_current_user
from utils.uow import UnitOfWork, get_uow

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), uow: UnitOfWork = Depends(get_uow)
):
    service = AuthService(uow)
    user = await service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный email или пароль"
        )
    access_token = service.create_access_token(data={"sub": user.email})
    refresh_token = await service.create_refresh_token(user_id=user.id)
    return Token(refresh_token=refresh_token.token, access_token=access_token)


@auth_router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister = Depends(), uow: UnitOfWork = Depends(get_uow)
):
    auth_service = AuthService(uow)
    user = await auth_service.register_user(user_data.username, user_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(user_id=user.id)
    if user_data.session_id:
        await LearningService(uow).initiate_user_learning_by_session_id(
            user.id, user_data.session_id
        )
    return Token(refresh_token=refresh_token.token, access_token=access_token)


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: RefreshTokenRequest, uow: UnitOfWork = Depends(get_uow)
):
    service = AuthService(uow)
    try:
        new_tokens = await service.refresh_access_token(token_request.refresh_token)
        return new_tokens
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера"
        )


@auth_router.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return current_user
