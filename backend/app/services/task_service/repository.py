from models.task import TaskModel
from services.base.repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TaskModel)
        self.session = session
