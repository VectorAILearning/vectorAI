import logging

from core.config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

log = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
)


async def send_verification_email(email: EmailStr, token: str):
    try:
        verification_link = f"{settings.DOMAIN}/verify_email?token={token}"
        html_content = f"""<p>Пожалуйста, подтвердите свой адрес электронной почты, перейдя по этой ссылке: <a href="{verification_link}">Подтвердить почту</a></p>"""
        log.info(html_content)

        message = MessageSchema(
            subject="Подтверждение электронной почты",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        log.error(f"Error sending email: {e}", exc_info=True)


async def send_password_reset_email(email_to: EmailStr, token: str):
    try:
        reset_url = f"{settings.DOMAIN}/reset_password?token={token}"
        html_content = f"""<p>Для сброса пароля, пожалуйста, перейдите по следующей ссылке: <a href="{reset_url}">Сбросить пароль</a></p>"""
        log.info(html_content)

        message = MessageSchema(
            subject="Сброс пароля",
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        log.error(f"Error sending email: {e}", exc_info=True)
