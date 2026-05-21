from __future__ import annotations

import logging
from email.mime.text import MIMEText

from core.config import get_settings

logger = logging.getLogger("servicios_cine.email")


async def send_password_reset_email(email: str, reset_link: str) -> None:
    settings = get_settings()

    if not settings.smtp_host:
        logger.info(
            "DEV EMAIL — Password reset for %s: %s",
            email,
            reset_link,
        )
        return

    subject = "Restablece tu contraseña - AILinkCinema"
    body = f"""Haz clic en el siguiente enlace para restablecer tu contraseña:

{reset_link}

Si no solicitaste este cambio, ignora este mensaje.

El enlace expira en {settings.password_reset_token_ttl_minutes} minutos.
"""
    await _send_smtp(email, subject, body)


async def _send_smtp(recipient: str, subject: str, body: str) -> None:
    import ssl

    import aiosmtplib

    settings = get_settings()
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = recipient

    use_tls = settings.smtp_tls
    smtp_class = aiosmtplib.SMTP_SSL if use_tls else aiosmtplib.SMTP

    async with smtp_class(
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        use_tls=use_tls,
        tls_context=ssl.create_default_context() if use_tls else None,
    ) as smtp:
        if settings.smtp_user and settings.smtp_password:
            await smtp.login(settings.smtp_user, settings.smtp_password)
        await smtp.send_message(msg)

    logger.info("Password reset email sent to %s via SMTP", recipient)
