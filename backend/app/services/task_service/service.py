import uuid

from models.task import TaskModel
from schemas.task import TaskIn, TaskOut, TaskPatch
from utils.uow import UnitOfWork


class TaskService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def get_task(self, task_id: str) -> TaskOut:
        task_db = await self.uow.task_repo.get_by_id(task_id)
        return TaskOut.model_validate(task_db)

    async def create_task(self, task: TaskIn) -> TaskOut:
        task_db = await self.uow.task_repo.save(
            TaskModel(**task.model_dump(mode="python"))
        )
        await self.uow.session.commit()
        await self.uow.session.refresh(task_db)
        return TaskOut.model_validate(task_db)

    async def update_task(self, task: TaskModel) -> TaskOut:
        await self.uow.session.commit()
        await self.uow.session.refresh(task)
        return TaskOut.model_validate(task)

    async def partial_update_task(
        self, task_id: str | uuid.UUID, patch: TaskPatch
    ) -> TaskOut:
        task_db = await self.uow.task_repo.get_by_id(task_id)
        if not task_db:
            raise Exception("Task not found")
        patch_data = patch.model_dump(exclude_unset=True)
        for key, value in patch_data.items():
            setattr(task_db, key, value)
        await self.uow.session.commit()
        await self.uow.session.refresh(task_db)
        return TaskOut.model_validate(task_db)
