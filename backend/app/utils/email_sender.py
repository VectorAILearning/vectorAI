from core.config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
)


async def send_verification_email(email: str, token: str):
    verification_link = f"{settings.DOMAIN}/api/v1/auth/verify-email?token={token}"
    html_content = f"""<p>Пожалуйста, подтвердите свой адрес электронной почты, перейдя по этой ссылке: <a href=\"{verification_link}\">Подтвердить почту</a></p>"""
    print(html_content)
    # message = MessageSchema(
    #     subject="Подтверждение электронной почты",
    #     recipients=[email],
    #     html=html_content,
    #     subtype="html",
    # )
    #
    # fm = FastMail(conf)
    # await fm.send_message(message)
