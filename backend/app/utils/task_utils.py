import asyncio
from typing import Any, Optional


async def wait_for_task_in_db(
    task_repo, task_id: Any, retries: int = 5, delay: float = 0.2
) -> Optional[Any]:
    """
    Ожидает появления задачи в БД по id. Делает retries попыток с задержкой delay секунд.
    Возвращает задачу или None, если не найдено.
    """
    for _ in range(retries):
        task = await task_repo.get_by_id(task_id)
        if task:
            return task
        await asyncio.sleep(delay)
    return None
