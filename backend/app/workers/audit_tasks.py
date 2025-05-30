import logging
import time
import uuid

from agents.audit_agent import AuditAgent
from services import get_cache_service
from services.audit_service.service import AuditDialogService
# from services.audit_service.service import get_audit_service
from services.message_bus import push_and_publish
from utils.uow import uow_context

log = logging.getLogger(__name__)


def _msg(who: str, text: str, type_: str = "chat") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "ts": time.time(),
        "who": who,
        "text": text,
        "type": type_,
    }


# TODO: Дописать создание обучения
async def audit_full_pipeline_task(ctx, sid: str, history: str):
    log.info("pipeline start %s", sid)

    await push_and_publish(sid, _msg("bot", "Анализируем ваши предпочтения…"))
    async with uow_context() as uow:
        audit_service = AuditDialogService(uow=uow, redis_service=get_cache_service(), agent=AuditAgent())
    user_preference = audit_service.create_user_preference_by_audit_history(history)
    await push_and_publish(
        sid, _msg("system", f"Предпочтение пользователя: {user_preference}", "system")
    )
    await push_and_publish(sid, _msg("bot", "Собираем для вас индивидуальный курс…"))

    await push_and_publish(
        sid,
        _msg("bot", f'Курс «{course["title"]}» готов! Ознакомьтесь с деталями.'),
    )
    await push_and_publish(sid, _msg("system", "Курс создан", "course_created_done"))

    log.info("pipeline done %s", sid)
