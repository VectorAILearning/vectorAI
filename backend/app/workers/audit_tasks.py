import logging
import time
import uuid

from services.audit_service.service import get_audit_service
from services.message_bus import push_and_publish

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
    audit_service = await get_audit_service()
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
