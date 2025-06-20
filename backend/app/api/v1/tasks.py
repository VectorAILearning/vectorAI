from core.database import get_async_session
from fastapi import APIRouter, Depends
from models import UserModel
from schemas.task import TaskOut
from services.task_service.service import get_task_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth_utils import is_admin

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get("/", response_model=list[TaskOut])
async def get_all_tasks(
    # current_user: UserModel = is_admin,
    async_session: AsyncSession = Depends(get_async_session),
):
    task_service = get_task_service(async_session)
    tasks_db = await task_service.task_repo.list()
    return [TaskOut.model_validate(task) for task in tasks_db]
