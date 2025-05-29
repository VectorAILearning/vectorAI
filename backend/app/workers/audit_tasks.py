import json
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

from agents.audit_agent import AuditAgent
from agents.plan_agent import CoursePlanAgent
from core.broadcast import broadcaster
from services import get_cache_service
from services.audit_service.create_course_by_audit_service import (
    create_course_from_json,
)


async def audit_full_pipeline_task(
    ctx, session_id: str, history: str, client_prompt: str
):
    logging.info(f"[audit_full_pipeline_task] START session_id={session_id}")
    redis_service = get_cache_service()
    bot_msg = {"who": "bot", "text": "Готовим ваш профиль...", "type": "chat"}
    await redis_service.add_message(session_id, bot_msg)
    await broadcaster.publish(channel=f"chat_{session_id}", message=json.dumps(bot_msg))
    logging.info(
        f"[audit_full_pipeline_task] Published 'Готовим ваш профиль...' for session_id={session_id}"
    )

    profile_summary = await generate_profile_task(
        ctx, session_id, history, client_prompt
    )
    logging.info(
        f"[audit_full_pipeline_task] Profile summary generated for session_id={session_id}"
    )

    bot_msg2 = {
        "who": "bot",
        "text": "Собираем для вас индивидуальный курс...",
        "type": "chat",
    }
    await redis_service.add_message(session_id, bot_msg2)
    await broadcaster.publish(
        channel=f"chat_{session_id}", message=json.dumps(bot_msg2)
    )
    logging.info(
        f"[audit_full_pipeline_task] Published 'Собираем для вас индивидуальный курс...' for session_id={session_id}"
    )

    await generate_course_task(ctx, session_id, profile_summary)
    logging.info(f"[audit_full_pipeline_task] END session_id={session_id}")


async def generate_profile_task(ctx, session_id: str, history: str, client_prompt: str):
    logging.info(f"[generate_profile_task] START session_id={session_id}")
    agent = AuditAgent()
    profile_summary = agent.call_llm(
        agent.summarize_profile_prompt(history, client_prompt)
    )
    redis_service = get_cache_service()
    await redis_service.add_message(
        session_id,
        {
            "who": "system",
            "text": f"Профиль пользователя сгенерирован: {profile_summary}",
            "type": "system",
        },
    )
    logging.info(f"[generate_profile_task] END session_id={session_id}")
    return profile_summary


async def generate_course_task(ctx, session_id: str, profile_summary: str):
    logging.info(f"[generate_course_task] START session_id={session_id}")
    redis_service = get_cache_service()
    try:
        course_plan = CoursePlanAgent().generate_course(profile_summary)

        created_course = await create_course_from_json(course_plan, "test")
        chat_msg = {
            "who": "bot",
            "text": f'Курс "{created_course.get("title")}" готов! Можете ознакомиться с деталями.',
            "type": "chat",
        }
        await redis_service.add_message(session_id, chat_msg)
        await broadcaster.publish(
            channel=f"chat_{session_id}", message=json.dumps(chat_msg)
        )

        system_msg = {
            "who": "system",
            "text": "Курс создан",
            "type": "course_created_done",
        }
        await redis_service.add_message(session_id, system_msg)
        await broadcaster.publish(
            channel=f"chat_{session_id}", message=json.dumps(system_msg)
        )
        logging.info(f"[generate_course_task] END session_id={session_id}")
    except Exception as e:
        logging.exception(f"[generate_course_task] ERROR session_id={session_id}: {e}")
        raise
