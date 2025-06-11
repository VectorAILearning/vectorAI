from fastapi import APIRouter, Depends
from models import UserModel
from schemas.task import TaskOut
from services.task_service.service import TaskService
from utils.auth_utils import is_admin
from utils.uow import UnitOfWork, get_uow

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get("/", response_model=list[TaskOut])
async def get_all_tasks(
    # current_user: UserModel = is_admin,
    uow: UnitOfWork = Depends(get_uow),
):
    tasks_db = await uow.task_repo.list()
    return [TaskOut.model_validate(task) for task in tasks_db]
