from fastapi import APIRouter, Depends
from schemas.task import TaskOut
from services.task_service.service import TaskService
from utils.uow import UnitOfWork, get_uow

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get("/", response_model=list[TaskOut])
async def get_all_tasks(uow: UnitOfWork = Depends(get_uow)):
    service = TaskService(uow)
    tasks_db = await uow.task_repo.list()
    return [TaskOut.model_validate(task) for task in tasks_db]
