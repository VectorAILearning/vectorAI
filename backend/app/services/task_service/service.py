from models.task import TaskModel
from schemas.task import TaskIn, TaskOut
from utils.uow import UnitOfWork


class TaskService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def create_task(self, task: TaskIn) -> TaskOut:
        task_db = await self.uow.task_repo.save(TaskModel(**task.model_dump()))
        await self.uow.session.commit()
        await self.uow.session.refresh(task_db)
        return TaskOut.model_validate(task_db)
