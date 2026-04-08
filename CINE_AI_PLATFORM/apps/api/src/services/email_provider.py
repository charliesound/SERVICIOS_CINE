"""SMTP email provider for follow-up delivery.

Supports Gmail SMTP and any generic SMTP server.
Uses only stdlib (smtplib, email) — no external dependencies.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class EmailSendResult:
    """Result of an email send attempt."""

    def __init__(
        self,
        success: bool,
        message_id: Optional[str] = None,
        error: Optional[str] = None,
        provider_response: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message_id = message_id
        self.error = error
        self.provider_response = provider_response or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message_id": self.message_id,
            "error": self.error,
            "provider_response": self.provider_response,
        }


class SMTPProvider:
    """SMTP email provider — works with Gmail and any standard SMTP server."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: int = 30,
        allow_self_signed: bool = False,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.allow_self_signed = allow_self_signed

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str,
        from_email: str,
        reply_to: Optional[str] = None,
        html: Optional[str] = None,
    ) -> EmailSendResult:
        """Send an email via SMTP.

        Returns EmailSendResult with success status, message_id, and error if any.
        """
        try:
            msg = self._build_message(to_email, subject, body, from_name, from_email, reply_to, html)

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                if self.use_tls:
                    server.starttls()

            server.login(self.username, self.password)
            send_result = server.sendmail(from_email, [to_email], msg.as_string())
            server.quit()

            # send_result is empty dict on success
            if send_result:
                error_details = str(send_result)
                logger.error("SMTP send had failures: %s", error_details)
                return EmailSendResult(
                    success=False,
                    error=f"SMTP partial failure: {error_details[:200]}",
                )

            # Extract message-id from the message headers
            message_id = msg.get("Message-ID")

            logger.info(
                "Email sent to %s — subject: %s — message_id: %s",
                to_email,
                subject,
                message_id,
            )

            return EmailSendResult(
                success=True,
                message_id=message_id,
                provider_response={"smtp_host": self.host, "smtp_port": self.port},
            )

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {e}"
            logger.error(error_msg)
            return EmailSendResult(success=False, error=error_msg)

        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP connection failed: {e}"
            logger.error(error_msg)
            return EmailSendResult(success=False, error=error_msg)

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            logger.error(error_msg)
            return EmailSendResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Unexpected error sending email: {e}"
            logger.error(error_msg)
            return EmailSendResult(success=False, error=error_msg)

    def test_connection(self) -> EmailSendResult:
        """Test SMTP connectivity and authentication without sending an email."""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                if self.use_tls:
                    server.starttls()

            server.login(self.username, self.password)
            server.quit()

            return EmailSendResult(
                success=True,
                provider_response={"smtp_host": self.host, "smtp_port": self.port},
            )

        except smtplib.SMTPAuthenticationError as e:
            return EmailSendResult(success=False, error=f"Authentication failed: {e}")
        except smtplib.SMTPConnectError as e:
            return EmailSendResult(success=False, error=f"Connection failed: {e}")
        except Exception as e:
            return EmailSendResult(success=False, error=f"Test failed: {e}")

    def _build_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str,
        from_email: str,
        reply_to: Optional[str] = None,
        html: Optional[str] = None,
    ) -> MIMEMultipart:
        """Build a MIME email message."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email

        if reply_to:
            msg["Reply-To"] = reply_to

        import socket
        import uuid
        msg["Message-ID"] = f"<{uuid.uuid4().hex}@{socket.getfqdn()}>"

        # Plain text part
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # HTML part if provided
        if html:
            msg.attach(MIMEText(html, "html", "utf-8"))

        return msg
