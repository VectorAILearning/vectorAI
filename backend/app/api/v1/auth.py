from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import Token, UserRegister
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
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister = Depends(), uow: UnitOfWork = Depends(get_uow)
):
    auth_service = AuthService(uow)
    user = await auth_service.register_user(user_data.username, user_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    if user_data.session_id:
        await LearningService(uow).initiate_user_learning_by_session_id(
            user.id, user_data.session_id
        )

    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return current_user
