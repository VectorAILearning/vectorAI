import logging
from services.content_service.service import ContentService
from utils.uow import uow_context
from models import ContentModel, LessonModel, ModuleModel, CourseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

log = logging.getLogger(__name__)

async def generate_block_content(ctx, block_id: str, lesson_id: str, **kwargs):
    async with uow_context() as uow:
        block = await uow.session.get(
            ContentModel, block_id,
            options=[
                selectinload(ContentModel.lesson)
                .selectinload(LessonModel.module)
                .selectinload(ModuleModel.course)
                .selectinload(CourseModel.modules)
                .selectinload(ModuleModel.lessons)
                .selectinload(LessonModel.contents)
            ]
        )
        lesson = block.lesson if block else None
        if not block or not lesson:
            log.error(f"Block or lesson not found: block_id={block_id}, lesson_id={lesson_id}")
            return
        log.debug(f"Начинаю генерацию контента для блока: block_id={block_id}, type={block.type}, description={block.description}, goal={block.goal}")
        try:
            await ContentService(uow).generate_content_by_block(block)
            log.debug(f"Контент успешно сгенерирован и сохранён для блока: block_id={block_id}")
        except Exception as e:
            log.exception(f"Ошибка при генерации контента для блока: block_id={block_id}, error={e}")
            return
        next_block = await uow.session.execute(
            select(ContentModel)
            .where(ContentModel.lesson_id == lesson_id)
            .where(ContentModel.position == block.position + 1)
        )
        next_block = next_block.scalar_one_or_none()
        if next_block:
            log.info(f"Следующий блок найден: id={next_block.id}, type={next_block.type}, position={next_block.position}")
            await ctx['arq_queue'].enqueue_job(
                'generate_block_content',
                block_id=str(next_block.id),
                lesson_id=lesson_id,
                _queue_name='course_generation'
            )
            
            log.info(f"Задача на генерацию контента для блока {next_block.id} поставлена в очередь")
        else:
            log.info(f"Следующего блока не найдено для lesson_id={lesson_id}, position={block.position + 1}") 