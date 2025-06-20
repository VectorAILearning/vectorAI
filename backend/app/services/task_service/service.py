import uuid

from models.task import TaskModel
from schemas.task import TaskIn, TaskOut, TaskPatch
from services.task_service.repository import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession


def get_task_service(session: AsyncSession) -> "TaskService":
    """
    Фабричный метод для создания TaskService
    """
    task_repo = TaskRepository(session)
    return TaskService(session, task_repo)


class TaskService:
    def __init__(
        self,
        session: AsyncSession,
        task_repo: TaskRepository,
    ):
        self.session = session
        self.task_repo = task_repo

    async def get_task(self, task_id: str) -> TaskOut:
        task_db = await self.task_repo.get_by_id(task_id)
        return TaskOut.model_validate(task_db)

    async def create_task(self, task: TaskIn) -> TaskOut:
        task_db = await self.task_repo.save(TaskModel(**task.model_dump(mode="python")))
        await self.session.commit()
        await self.session.refresh(task_db)
        return TaskOut.model_validate(task_db)

    async def update_task(self, task: TaskModel) -> TaskOut:
        await self.session.commit()
        await self.session.refresh(task)
        return TaskOut.model_validate(task)

    async def partial_update_task(
        self, task_id: str | uuid.UUID, patch: TaskPatch
    ) -> TaskOut:
        task_db = await self.task_repo.get_by_id(task_id)
        if not task_db:
            raise Exception("Task not found")
        patch_data = patch.model_dump(exclude_unset=True)
        for key, value in patch_data.items():
            setattr(task_db, key, value)
        await self.session.commit()
        await self.session.refresh(task_db)
        return TaskOut.model_validate(task_db)
