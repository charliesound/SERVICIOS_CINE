"""Follow-up send service — orchestrates email delivery for follow-ups.

Supports three modes:
- disabled: no sending, returns blocked status
- simulated: records simulation without sending
- smtp: sends real email via SMTP provider
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.services.email_provider import SMTPProvider, EmailSendResult
from src.services.email_templates import get_template

logger = logging.getLogger(__name__)


class FollowUpSendService:
    """Orchestrates follow-up email delivery with mode-aware behavior."""

    def __init__(
        self,
        store,
        send_mode: str = "simulated",
        auto_send_enabled: bool = False,
        smtp_provider: Optional[SMTPProvider] = None,
        from_name: str = "CID",
        from_email: str = "noreply@cid.example.com",
        reply_to: Optional[str] = None,
        test_recipient: Optional[str] = None,
    ):
        self.store = store
        self.send_mode = send_mode
        self.auto_send_enabled = auto_send_enabled
        self.smtp_provider = smtp_provider
        self.from_name = from_name
        self.from_email = from_email
        self.reply_to = reply_to
        self.test_recipient = test_recipient

    def send_followup(self, followup_id: str) -> Dict[str, Any]:
        """Send a follow-up by ID.

        Returns dict with success status, mode, and result details.
        """
        followup = self.store.get(followup_id)
        if not followup:
            return {
                "success": False,
                "error": "Follow-up not found",
                "followup_id": followup_id,
            }

        if followup["status"] == "sent":
            return {
                "success": False,
                "error": "Follow-up already sent",
                "followup_id": followup_id,
            }

        if self.send_mode == "disabled":
            return self._record_blocked(followup_id, followup)

        if self.send_mode == "simulated":
            return self._record_simulated(followup_id, followup)

        if self.send_mode == "smtp":
            return self._send_smtp(followup_id, followup)

        return {
            "success": False,
            "error": f"Unknown send mode: {self.send_mode}",
            "followup_id": followup_id,
        }

    def retry_followup(self, followup_id: str) -> Dict[str, Any]:
        """Retry a failed or draft follow-up."""
        followup = self.store.get(followup_id)
        if not followup:
            return {
                "success": False,
                "error": "Follow-up not found",
                "followup_id": followup_id,
            }

        if followup["status"] not in ("failed", "draft", "queued"):
            return {
                "success": False,
                "error": f"Cannot retry follow-up with status: {followup['status']}",
                "followup_id": followup_id,
            }

        # Reset status for retry
        self.store.update(followup_id, {
            "status": "queued",
            "last_error": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        return self.send_followup(followup_id)

    def test_smtp_connection(self) -> Dict[str, Any]:
        """Test SMTP connectivity and authentication."""
        if self.send_mode != "smtp":
            return {
                "success": False,
                "error": f"Send mode is '{self.send_mode}', not 'smtp'",
                "mode": self.send_mode,
            }

        if not self.smtp_provider:
            return {
                "success": False,
                "error": "SMTP provider not configured",
                "mode": self.send_mode,
            }

        result = self.smtp_provider.test_connection()
        return {
            "success": result.success,
            "mode": "smtp",
            "message_id": result.message_id,
            "error": result.error,
            "provider_response": result.provider_response,
        }

    def send_test_email(self, to_email: str) -> Dict[str, Any]:
        """Send a test email to verify full SMTP delivery."""
        if self.send_mode != "smtp":
            return {
                "success": False,
                "error": f"Send mode is '{self.send_mode}', not 'smtp'",
                "mode": self.send_mode,
            }

        if not self.smtp_provider:
            return {
                "success": False,
                "error": "SMTP provider not configured",
                "mode": self.send_mode,
            }

        result = self.smtp_provider.send(
            to_email=to_email,
            subject="CID — Test de configuración SMTP",
            body="Este es un email de prueba de CID — Cine Inteligente Digital.\nSi lo recibes, la configuración SMTP es correcta.",
            from_name=self.from_name,
            from_email=self.from_email,
            reply_to=self.reply_to,
        )

        return {
            "success": result.success,
            "mode": "smtp",
            "to_email": to_email,
            "message_id": result.message_id,
            "error": result.error,
            "provider_response": result.provider_response,
        }

    def generate_and_send(
        self,
        lead: Dict[str, Any],
        template_key: str = "cid_storyboard_ia_initial",
        campaign_key: str = "cid_storyboard_ia",
        auto_send: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Generate a follow-up from lead data and optionally send it.

        If auto_send is True and mode allows, sends immediately.
        Otherwise creates as draft.
        """
        template_fn = get_template(template_key)
        if not template_fn:
            return {
                "success": False,
                "error": f"Template not found: {template_key}",
            }

        subject, body = template_fn(lead)

        now = datetime.now(timezone.utc).isoformat()
        followup_id = f"fu_{lead.get('id', 'unknown')}_{now.replace(':', '').replace('-', '').replace('.', '')[:14]}"

        followup = {
            "id": followup_id,
            "lead_id": lead.get("id", ""),
            "campaign_key": campaign_key,
            "template_key": template_key,
            "channel": "email",
            "subject": subject,
            "body": body,
            "status": "draft",
            "scheduled_at": None,
            "sent_at": None,
            "last_error": None,
            "created_at": now,
            "updated_at": now,
        }

        created = self.store.create(followup)

        should_send = auto_send if auto_send is not None else self.auto_send_enabled

        if should_send and self.send_mode in ("smtp", "simulated"):
            send_result = self.send_followup(followup_id)
            created = self.store.get(followup_id) or created
            created["_send_result"] = send_result

        return {
            "success": True,
            "followup": created,
            "auto_sent": should_send,
        }

    def get_email_status(self) -> Dict[str, Any]:
        """Return current email configuration status."""
        smtp_configured = bool(
            self.smtp_provider
            and self.smtp_provider.host
            and self.smtp_provider.username
        )

        return {
            "send_mode": self.send_mode,
            "auto_send_enabled": self.auto_send_enabled,
            "smtp_configured": smtp_configured,
            "from_name": self.from_name,
            "from_email": self.from_email,
            "reply_to": self.reply_to,
            "test_recipient": self.test_recipient,
            "smtp_host": self.smtp_provider.host if self.smtp_provider else None,
            "smtp_port": self.smtp_provider.port if self.smtp_provider else None,
        }

    # --- Private methods ---

    def _record_blocked(self, followup_id: str, followup: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        self.store.update(followup_id, {
            "status": "skipped",
            "last_error": "Email sending is disabled (mode=disabled)",
            "updated_at": now,
        })
        return {
            "success": False,
            "mode": "disabled",
            "followup_id": followup_id,
            "error": "Email sending is disabled",
            "status": "skipped",
        }

    def _record_simulated(self, followup_id: str, followup: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        self.store.update(followup_id, {
            "status": "sent",
            "sent_at": now,
            "updated_at": now,
            "provider": "simulated",
            "delivery_mode": "simulated",
        })
        return {
            "success": True,
            "mode": "simulated",
            "followup_id": followup_id,
            "status": "sent",
            "sent_at": now,
            "note": "Email was simulated — not actually sent",
        }

    def _send_smtp(self, followup_id: str, followup: Dict[str, Any]) -> Dict[str, Any]:
        if not self.smtp_provider:
            now = datetime.now(timezone.utc).isoformat()
            self.store.update(followup_id, {
                "status": "failed",
                "last_error": "SMTP provider not configured",
                "updated_at": now,
            })
            return {
                "success": False,
                "mode": "smtp",
                "followup_id": followup_id,
                "error": "SMTP provider not configured",
                "status": "failed",
            }

        # Determine recipient
        recipient = followup.get("recipient_email", "")
        if not recipient:
            # Try to get from lead context — for now use test_recipient
            if self.test_recipient:
                recipient = self.test_recipient
            else:
                now = datetime.now(timezone.utc).isoformat()
                self.store.update(followup_id, {
                    "status": "failed",
                    "last_error": "No recipient email available",
                    "updated_at": now,
                })
                return {
                    "success": False,
                    "mode": "smtp",
                    "followup_id": followup_id,
                    "error": "No recipient email available",
                    "status": "failed",
                }

        # Mark as sending
        now = datetime.now(timezone.utc).isoformat()
        self.store.update(followup_id, {
            "status": "sending",
            "last_attempt_at": now,
            "updated_at": now,
        })

        # Send
        result = self.smtp_provider.send(
            to_email=recipient,
            subject=followup["subject"],
            body=followup["body"],
            from_name=self.from_name,
            from_email=self.from_email,
            reply_to=self.reply_to,
        )

        now = datetime.now(timezone.utc).isoformat()

        if result.success:
            self.store.update(followup_id, {
                "status": "sent",
                "sent_at": now,
                "provider": "smtp",
                "provider_message_id": result.message_id,
                "delivery_mode": "smtp",
                "delivery_details_json": str(result.provider_response),
                "last_error": None,
                "updated_at": now,
            })
            return {
                "success": True,
                "mode": "smtp",
                "followup_id": followup_id,
                "status": "sent",
                "sent_at": now,
                "message_id": result.message_id,
                "provider": "smtp",
                "provider_response": result.provider_response,
            }
        else:
            attempts = (followup.get("attempts_count") or 0) + 1
            self.store.update(followup_id, {
                "status": "failed",
                "last_error": result.error,
                "attempts_count": attempts,
                "last_attempt_at": now,
                "updated_at": now,
            })
            return {
                "success": False,
                "mode": "smtp",
                "followup_id": followup_id,
                "status": "failed",
                "error": result.error,
                "attempts": attempts,
            }
