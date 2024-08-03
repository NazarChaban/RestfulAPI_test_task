"""
This module provides functionality for sending emails using FastAPI-Mail.

It contains the `send_email` function which sends an email to the user with a link to verify their account.
"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Post Manager API",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify
    their account.

    :param email: Pass the email address to send the email to
    :param username: Pass the username of the user to be sent an email
    :param host: Pass the host name of the server to the email template
    :return: A coroutine object
    """
    try:
        token_verification = await auth_service.create_email_token(email)
        message = MessageSchema(
            subject='confirm your email',
            recipients=[email],
            template_body={
                'host': host,
                'username': username,
                'token': token_verification
            },
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_template.html')
    except ConnectionErrors as err:
        print(err)
