"""Follow-up V3 automation service — queue, retries, priorities, sequences.

Orchestrates:
1. Queue processing with priority ordering
2. Controlled retries with backoff
3. Sequence generation and eligibility
4. Safe processing with lock tokens
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from src.services.email_provider import SMTPProvider, EmailSendResult
from src.services.email_templates import get_template

logger = logging.getLogger(__name__)

# Errors that are retryable vs terminal
RETRYABLE_ERRORS = [
    "SMTP error",
    "SMTP connection failed",
    "SMTP partial failure",
    "Unexpected error",
    "timeout",
    "Connection",
]

TERMINAL_ERRORS = [
    "SMTP authentication failed",
    "No recipient email",
    "Template not found",
    "Follow-up already sent",
    "Follow-up not found",
]


def is_retryable_error(error: str) -> bool:
    """Determine if an error is retryable."""
    if not error:
        return False
    error_lower = error.lower()
    return any(term.lower() in error_lower for term in RETRYABLE_ERRORS)


class FollowUpAutomationService:
    """V3 automation service for follow-up queue, retries, priorities, and sequences."""

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
        # V3 settings
        automation_enabled: bool = True,
        retry_enabled: bool = True,
        max_attempts: int = 3,
        retry_base_minutes: int = 30,
        queue_batch_size: int = 20,
        auto_enqueue_on_generate: bool = True,
        sequence_cid_storyboard_enabled: bool = True,
    ):
        self.store = store
        self.send_mode = send_mode
        self.auto_send_enabled = auto_send_enabled
        self.smtp_provider = smtp_provider
        self.from_name = from_name
        self.from_email = from_email
        self.reply_to = reply_to
        self.test_recipient = test_recipient
        # V3 settings
        self.automation_enabled = automation_enabled
        self.retry_enabled = retry_enabled
        self.max_attempts = max_attempts
        self.retry_base_minutes = retry_base_minutes
        self.queue_batch_size = queue_batch_size
        self.auto_enqueue_on_generate = auto_enqueue_on_generate
        self.sequence_cid_storyboard_enabled = sequence_cid_storyboard_enabled

    def enqueue_followup(self, followup_id: str) -> Dict[str, Any]:
        """Enqueue a follow-up for processing."""
        followup = self.store.get(followup_id)
        if not followup:
            return {"success": False, "error": "Follow-up not found"}

        if followup.get("queue_status") in ("sent", "cancelled"):
            return {
                "success": False,
                "error": f"Cannot enqueue follow-up with status: {followup.get('queue_status')}",
            }

        now = datetime.now(timezone.utc).isoformat()
        self.store.update(followup_id, {
            "queue_status": "queued",
            "next_attempt_at": now,
            "updated_at": now,
        })

        return {"success": True, "followup_id": followup_id, "queue_status": "queued"}

    def process_queue(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """Process queued follow-ups in priority order.

        Returns summary of processed items.
        """
        if not self.automation_enabled:
            return {"success": False, "error": "Automation is disabled"}

        size = batch_size or self.queue_batch_size
        items = self.store.get_queue_items(batch_size=size)

        if not items:
            return {"success": True, "processed": 0, "message": "No items in queue"}

        results = []
        for item in items:
            result = self._process_single(item)
            results.append(result)

        sent = sum(1 for r in results if r.get("status") == "sent")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")

        return {
            "success": True,
            "processed": len(results),
            "sent": sent,
            "failed": failed,
            "skipped": skipped,
            "details": results,
        }

    def retry_followup(self, followup_id: str) -> Dict[str, Any]:
        """Retry a failed follow-up."""
        if not self.retry_enabled:
            return {"success": False, "error": "Retries are disabled"}

        followup = self.store.get(followup_id)
        if not followup:
            return {"success": False, "error": "Follow-up not found"}

        if followup.get("queue_status") not in ("failed", "skipped"):
            return {
                "success": False,
                "error": f"Cannot retry follow-up with status: {followup.get('queue_status')}",
            }

        now = datetime.now(timezone.utc).isoformat()
        self.store.update(followup_id, {
            "queue_status": "queued",
            "next_attempt_at": now,
            "terminal_reason": None,
            "updated_at": now,
        })

        return self._process_single(followup)

    def get_queue_status(self) -> Dict[str, Any]:
        """Return queue summary and configuration."""
        summary = self.store.get_queue_summary()
        return {
            "ok": True,
            "automation_enabled": self.automation_enabled,
            "send_mode": self.send_mode,
            "retry_enabled": self.retry_enabled,
            "max_attempts": self.max_attempts,
            "retry_base_minutes": self.retry_base_minutes,
            "queue_batch_size": self.queue_batch_size,
            "summary": summary,
        }

    def generate_sequence(
        self,
        lead: Dict[str, Any],
        campaign_key: str = "cid_storyboard_ia",
        sequence_key: str = "cid_storyboard_ia_sequence",
    ) -> Dict[str, Any]:
        """Generate the initial sequence of follow-ups for a lead.

        Creates step_1 (initial autoresponse) and schedules subsequent steps.
        """
        if not self.sequence_cid_storyboard_enabled:
            return {"success": False, "error": "Sequence generation is disabled"}

        steps = self._get_sequence_steps(campaign_key)
        created = []

        now = datetime.now(timezone.utc)

        for step in steps:
            step_index = step["step_index"]

            # Prevent duplicate steps
            if self.store.exists_for_lead_and_step(lead.get("id", ""), sequence_key, step_index):
                continue

            template_fn = get_template(step["template_key"])
            if not template_fn:
                logger.warning("Template not found: %s", step["template_key"])
                continue

            subject, body = template_fn(lead)

            delay_minutes = step.get("delay_minutes", 0)
            scheduled_for = (now + timedelta(minutes=delay_minutes)).isoformat()
            eligible_at = scheduled_for if delay_minutes > 0 else now.isoformat()

            followup_id = f"fu_{lead.get('id', 'unknown')}_{sequence_key}_{step_index}_{now.strftime('%Y%m%d%H%M%S')}"

            followup = {
                "id": followup_id,
                "lead_id": lead.get("id", ""),
                "campaign_key": campaign_key,
                "template_key": step["template_key"],
                "channel": "email",
                "subject": subject,
                "body": body,
                "status": "draft",
                "queue_status": "queued" if step_index == 1 else "queued",
                "scheduled_at": scheduled_for,
                "sent_at": None,
                "last_error": None,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "priority": lead.get("priority", "warm"),
                "sequence_key": sequence_key,
                "sequence_step": step_index,
                "scheduled_for": scheduled_for,
                "eligible_at": eligible_at,
                "generation_mode": "automatic",
                "max_attempts": self.max_attempts,
                "recipient_email": lead.get("email", ""),
                "from_email": self.from_email,
            }

            created_followup = self.store.create(followup)
            created.append(created_followup)

        return {
            "success": True,
            "sequence_key": sequence_key,
            "steps_generated": len(created),
            "followups": created,
        }

    def get_lead_sequences(self, lead_id: str) -> Dict[str, Any]:
        """Get all sequences and their steps for a lead."""
        # Get all follow-ups for this lead grouped by sequence_key
        all_followups = self.store.list(lead_id=lead_id, limit=200)

        sequences: Dict[str, List[Dict[str, Any]]] = {}
        for fu in all_followups:
            seq_key = fu.get("sequence_key")
            if not seq_key:
                continue
            if seq_key not in sequences:
                sequences[seq_key] = []
            sequences[seq_key].append(fu)

        # Sort each sequence by step
        for seq_key in sequences:
            sequences[seq_key].sort(key=lambda x: x.get("sequence_step") or 0)

        return {
            "ok": True,
            "lead_id": lead_id,
            "sequences": sequences,
        }

    # --- Private methods ---

    def _process_single(self, followup: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single follow-up from the queue."""
        followup_id = followup["id"]
        lock_token = str(uuid.uuid4())

        # Claim atomically
        claimed = self.store.claim_for_processing(followup_id, lock_token)
        if not claimed:
            return {
                "followup_id": followup_id,
                "status": "skipped",
                "reason": "Already claimed by another process",
            }

        # Check eligibility
        eligible_at = claimed.get("eligible_at")
        if eligible_at:
            try:
                eligible_time = datetime.fromisoformat(eligible_at)
                if eligible_time > datetime.now(timezone.utc):
                    now = datetime.now(timezone.utc).isoformat()
                    self.store.update(followup_id, {
                        "queue_status": "queued",
                        "processing_lock_token": None,
                        "next_attempt_at": eligible_at,
                        "updated_at": now,
                    })
                    return {
                        "followup_id": followup_id,
                        "status": "skipped",
                        "reason": "Not yet eligible",
                        "eligible_at": eligible_at,
                    }
            except (ValueError, TypeError):
                pass

        # Check max attempts
        attempts = claimed.get("attempts_count", 0)
        max_attempts = claimed.get("max_attempts", self.max_attempts)
        if attempts >= max_attempts:
            now = datetime.now(timezone.utc).isoformat()
            self.store.update(followup_id, {
                "queue_status": "skipped",
                "terminal_reason": "max_attempts_reached",
                "processing_lock_token": None,
                "updated_at": now,
            })
            return {
                "followup_id": followup_id,
                "status": "skipped",
                "reason": "Max attempts reached",
                "attempts": attempts,
            }

        # Determine recipient
        recipient = claimed.get("recipient_email", "")
        if not recipient:
            if self.test_recipient:
                recipient = self.test_recipient
            else:
                now = datetime.now(timezone.utc).isoformat()
                self.store.update(followup_id, {
                    "queue_status": "failed",
                    "last_error": "No recipient email available",
                    "terminal_reason": "no_recipient",
                    "processing_lock_token": None,
                    "updated_at": now,
                })
                return {
                    "followup_id": followup_id,
                    "status": "failed",
                    "error": "No recipient email",
                }

        # Send based on mode
        if self.send_mode == "disabled":
            now = datetime.now(timezone.utc).isoformat()
            self.store.update(followup_id, {
                "queue_status": "skipped",
                "terminal_reason": "sending_disabled",
                "processing_lock_token": None,
                "updated_at": now,
            })
            return {"followup_id": followup_id, "status": "skipped", "reason": "Sending disabled"}

        if self.send_mode == "simulated":
            now = datetime.now(timezone.utc).isoformat()
            self.store.update(followup_id, {
                "queue_status": "sent",
                "status": "sent",
                "sent_at": now,
                "provider": "simulated",
                "delivery_mode": "simulated",
                "attempts_count": attempts + 1,
                "last_attempt_at": now,
                "processing_lock_token": None,
                "updated_at": now,
            })
            return {
                "followup_id": followup_id,
                "status": "sent",
                "mode": "simulated",
                "sent_at": now,
            }

        if self.send_mode == "smtp":
            return self._send_smtp(followup_id, claimed, recipient, attempts, lock_token)

        # Unknown mode
        now = datetime.now(timezone.utc).isoformat()
        self.store.update(followup_id, {
            "queue_status": "failed",
            "last_error": f"Unknown send mode: {self.send_mode}",
            "processing_lock_token": None,
            "updated_at": now,
        })
        return {
            "followup_id": followup_id,
            "status": "failed",
            "error": f"Unknown send mode: {self.send_mode}",
        }

    def _send_smtp(
        self,
        followup_id: str,
        followup: Dict[str, Any],
        recipient: str,
        attempts: int,
        lock_token: str,
    ) -> Dict[str, Any]:
        """Send via SMTP and record result."""
        if not self.smtp_provider:
            now = datetime.now(timezone.utc).isoformat()
            self.store.update(followup_id, {
                "queue_status": "failed",
                "last_error": "SMTP provider not configured",
                "terminal_reason": "smtp_not_configured",
                "processing_lock_token": None,
                "updated_at": now,
            })
            return {
                "followup_id": followup_id,
                "status": "failed",
                "error": "SMTP not configured",
            }

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
                "queue_status": "sent",
                "status": "sent",
                "sent_at": now,
                "provider": "smtp",
                "provider_message_id": result.message_id,
                "delivery_mode": "smtp",
                "delivery_details_json": str(result.provider_response),
                "attempts_count": attempts + 1,
                "last_attempt_at": now,
                "last_error": None,
                "processing_lock_token": None,
                "updated_at": now,
            })

            # Schedule next sequence step if applicable
            self._schedule_next_step(followup)

            return {
                "followup_id": followup_id,
                "status": "sent",
                "mode": "smtp",
                "sent_at": now,
                "message_id": result.message_id,
            }
        else:
            new_attempts = attempts + 1
            error = result.error or "Unknown error"
            retryable = is_retryable_error(error)

            update_fields: Dict[str, Any] = {
                "attempts_count": new_attempts,
                "last_attempt_at": now,
                "last_error": error,
                "processing_lock_token": None,
                "updated_at": now,
            }

            if retryable and new_attempts < followup.get("max_attempts", self.max_attempts):
                # Schedule retry with backoff
                backoff_minutes = self.retry_base_minutes * (2 ** (new_attempts - 1))
                next_attempt = (
                    datetime.now(timezone.utc) + timedelta(minutes=backoff_minutes)
                ).isoformat()
                update_fields["queue_status"] = "queued"
                update_fields["next_attempt_at"] = next_attempt
                queue_status = "queued"
            else:
                update_fields["queue_status"] = "failed"
                update_fields["terminal_reason"] = "max_attempts_reached" if not retryable else "retry_exhausted"
                queue_status = "failed"

            self.store.update(followup_id, update_fields)

            return {
                "followup_id": followup_id,
                "status": "failed",
                "error": error,
                "retryable": retryable,
                "attempts": new_attempts,
                "queue_status": queue_status,
                "next_attempt_at": update_fields.get("next_attempt_at"),
            }

    def _schedule_next_step(self, sent_followup: Dict[str, Any]) -> None:
        """Schedule the next step in a sequence after successful send."""
        sequence_key = sent_followup.get("sequence_key")
        current_step = sent_followup.get("sequence_step")
        lead_id = sent_followup.get("lead_id")

        if not sequence_key or current_step is None or not lead_id:
            return

        next_step = current_step + 1

        # Check if next step already exists
        if self.store.exists_for_lead_and_step(lead_id, sequence_key, next_step):
            return

        # Get sequence definition
        campaign_key = sent_followup.get("campaign_key", "cid_storyboard_ia")
        steps = self._get_sequence_steps(campaign_key)

        step_def = None
        for s in steps:
            if s["step_index"] == next_step:
                step_def = s
                break

        if not step_def:
            return

        # Create the next step follow-up
        lead = {
            "id": lead_id,
            "full_name": "",
            "email": sent_followup.get("recipient_email", ""),
            "company": "",
        }

        template_fn = get_template(step_def["template_key"])
        if not template_fn:
            return

        subject, body = template_fn(lead)

        now = datetime.now(timezone.utc)
        delay_minutes = step_def.get("delay_minutes", 0)
        scheduled_for = (now + timedelta(minutes=delay_minutes)).isoformat()
        eligible_at = scheduled_for if delay_minutes > 0 else now.isoformat()

        followup_id = f"fu_{lead_id}_{sequence_key}_{next_step}_{now.strftime('%Y%m%d%H%M%S')}"

        followup = {
            "id": followup_id,
            "lead_id": lead_id,
            "campaign_key": campaign_key,
            "template_key": step_def["template_key"],
            "channel": "email",
            "subject": subject,
            "body": body,
            "status": "draft",
            "queue_status": "queued",
            "scheduled_at": scheduled_for,
            "sent_at": None,
            "last_error": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "priority": sent_followup.get("priority", "warm"),
            "sequence_key": sequence_key,
            "sequence_step": next_step,
            "scheduled_for": scheduled_for,
            "eligible_at": eligible_at,
            "generation_mode": "automatic",
            "max_attempts": self.max_attempts,
            "recipient_email": lead.get("email", ""),
            "from_email": self.from_email,
        }

        self.store.create(followup)
        logger.info(
            "Scheduled sequence step %d for lead %s — followup %s",
            next_step,
            lead_id,
            followup_id,
        )

    def _get_sequence_steps(self, campaign_key: str) -> List[Dict[str, Any]]:
        """Return sequence steps for a campaign."""
        if campaign_key == "cid_storyboard_ia":
            return [
                {
                    "step_index": 1,
                    "template_key": "cid_storyboard_ia_initial",
                    "delay_minutes": 0,
                    "description": "Autorespuesta inicial",
                },
                {
                    "step_index": 2,
                    "template_key": "cid_storyboard_ia_initial",  # Reuse for V3; customize later
                    "delay_minutes": 4320,  # 3 days
                    "description": "Recordatorio suave",
                },
                {
                    "step_index": 3,
                    "template_key": "cid_storyboard_ia_initial",
                    "delay_minutes": 10080,  # 7 days after step 2
                    "description": "Cierre amable / invitación final",
                },
            ]
        return []
