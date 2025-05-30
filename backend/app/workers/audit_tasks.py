import logging, time, uuid
from agents.audit_agent import AuditAgent
from agents.plan_agent import CoursePlanAgent
from services.message_bus import push_and_publish
from services.audit_service.create_course_by_audit_service import (
    create_course_from_json,
)

log = logging.getLogger(__name__)


def _msg(who: str, text: str, type_: str = "chat") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "ts": time.time(),
        "who": who,
        "text": text,
        "type": type_,
    }


async def audit_full_pipeline_task(_, sid: str, history: str, client_prompt: str):
    log.info("pipeline start %s", sid)

    await push_and_publish(sid, _msg("bot", "Готовим ваш профиль…"))
    profile = await _generate_profile(sid, history, client_prompt)

    await push_and_publish(sid, _msg("bot", "Собираем для вас индивидуальный курс…"))
    await _generate_course(sid, profile)

    log.info("pipeline done %s", sid)


async def _generate_profile(sid: str, history: str, prompt: str) -> str:
    summary = AuditAgent().call_llm(
        AuditAgent.summarize_profile_prompt(history, prompt)
    )
    await push_and_publish(
        sid, _msg("system", f"Профиль пользователя: {summary}", "system")
    )
    return summary


async def _generate_course(sid: str, profile: str):
    try:
        plan = CoursePlanAgent().generate_course(profile)
        course = await create_course_from_json(plan, "test")

        await push_and_publish(
            sid,
            _msg("bot", f'Курс «{course["title"]}» готов! Ознакомьтесь с деталями.'),
        )
        await push_and_publish(
            sid, _msg("system", "Курс создан", "course_created_done")
        )
    except Exception:
        log.exception("course generation failed for %s", sid)
        raise
