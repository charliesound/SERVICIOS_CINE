"""Follow-up V3 automation routes.

Endpoints:
- GET    /api/followups/queue
- POST   /api/followups/{followup_id}/enqueue
- POST   /api/followups/process-queue
- POST   /api/followups/{followup_id}/retry
- GET    /api/leads/{lead_id}/followups
- GET    /api/leads/{lead_id}/sequences
- POST   /api/leads/{lead_id}/sequences/generate
- GET    /api/followups/automation-status
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel


def create_followup_v3_routes(automation_service) -> APIRouter:
    router = APIRouter(prefix="/api/followups", tags=["followups-v3"])

    class CreateFollowupRequest(BaseModel):
        lead_id: str
        template_key: str = "cid_storyboard_ia_initial"
        campaign_key: str = "cid_storyboard_ia"
        recipient_email: Optional[str] = None
        subject: Optional[str] = None
        body: Optional[str] = None
        auto_send: bool = False
        priority: str = "warm"

    class UpdateFollowupRequest(BaseModel):
        status: Optional[str] = None
        subject: Optional[str] = None
        body: Optional[str] = None
        scheduled_at: Optional[str] = None
        priority: Optional[str] = None

    class GenerateSequenceRequest(BaseModel):
        campaign_key: str = "cid_storyboard_ia"
        sequence_key: str = "cid_storyboard_ia_sequence"

    class TestEmailRequest(BaseModel):
        to_email: str

    # --- Standard follow-up endpoints ---

    @router.get("")
    def list_followups(
        lead_id: Optional[str] = Query(None),
        campaign_key: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
        queue_status: Optional[str] = Query(None),
        priority: Optional[str] = Query(None),
        limit: int = Query(50, le=200),
        offset: int = Query(0, ge=0),
    ):
        items = automation_service.store.list(
            lead_id=lead_id,
            campaign_key=campaign_key,
            status=status,
            queue_status=queue_status,
            priority=priority,
            limit=limit,
            offset=offset,
        )
        total = automation_service.store.count(
            lead_id=lead_id,
            campaign_key=campaign_key,
            status=status,
            queue_status=queue_status,
            priority=priority,
        )
        return {
            "ok": True,
            "followups": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @router.get("/{followup_id}")
    def get_followup(followup_id: str):
        followup = automation_service.store.get(followup_id)
        if not followup:
            return {"ok": False, "error": "Follow-up not found"}, 404
        return {"ok": True, "followup": followup}

    @router.post("")
    def create_followup(req: CreateFollowupRequest):
        from src.services.email_templates import get_template

        template_fn = get_template(req.template_key)
        if not template_fn:
            return {"ok": False, "error": f"Template not found: {req.template_key}"}, 400

        lead = {
            "id": req.lead_id,
            "full_name": "",
            "email": req.recipient_email or "",
            "company": "",
        }
        subject, body = template_fn(lead)

        if req.subject:
            subject = req.subject
        if req.body:
            body = req.body

        now = datetime.now(timezone.utc).isoformat()
        followup_id = f"fu_{req.lead_id}_{now.replace(':', '').replace('-', '').replace('.', '')[:14]}"

        followup = {
            "id": followup_id,
            "lead_id": req.lead_id,
            "campaign_key": req.campaign_key,
            "template_key": req.template_key,
            "channel": "email",
            "subject": subject,
            "body": body,
            "status": "draft",
            "queue_status": "queued" if req.auto_send else "queued",
            "scheduled_at": None,
            "sent_at": None,
            "last_error": None,
            "created_at": now,
            "updated_at": now,
            "priority": req.priority,
            "generation_mode": "manual",
            "max_attempts": automation_service.max_attempts,
            "recipient_email": req.recipient_email,
            "from_email": automation_service.from_email,
        }

        created = automation_service.store.create(followup)

        auto_sent = False
        if req.auto_send:
            result = automation_service._process_single(created)
            created = automation_service.store.get(followup_id) or created
            auto_sent = result.get("status") == "sent"

        return {
            "ok": True,
            "followup": created,
            "auto_sent": auto_sent,
        }

    @router.patch("/{followup_id}")
    def update_followup(followup_id: str, req: UpdateFollowupRequest):
        followup = automation_service.store.get(followup_id)
        if not followup:
            return {"ok": False, "error": "Follow-up not found"}, 404

        updates = req.model_dump(exclude_none=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        updated = automation_service.store.update(followup_id, updates)
        return {"ok": True, "followup": updated}

    # --- V3 Queue endpoints ---

    @router.get("/queue")
    def get_queue(
        queue_status: Optional[str] = Query(None),
        priority: Optional[str] = Query(None),
        limit: int = Query(50, le=200),
        offset: int = Query(0, ge=0),
    ):
        items = automation_service.store.list(
            queue_status=queue_status,
            priority=priority,
            limit=limit,
            offset=offset,
        )
        summary = automation_service.store.get_queue_summary()
        return {
            "ok": True,
            "queue": items,
            "summary": summary,
        }

    @router.post("/{followup_id}/enqueue")
    def enqueue_followup(followup_id: str):
        result = automation_service.enqueue_followup(followup_id)
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.post("/process-queue")
    def process_queue(batch_size: int = Query(20, ge=1, le=100)):
        result = automation_service.process_queue(batch_size=batch_size)
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.post("/{followup_id}/retry")
    def retry_followup(followup_id: str):
        result = automation_service.retry_followup(followup_id)
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.post("/{followup_id}/send")
    def send_followup(followup_id: str):
        result = automation_service._process_single(
            automation_service.store.get(followup_id) or {"id": followup_id}
        )
        status_code = 200 if result.get("status") == "sent" else 400
        return {"ok": result.get("status") == "sent", **result}, status_code

    # --- Lead endpoints ---

    @router.get("/leads/{lead_id}/followups")
    def get_lead_followups(lead_id: str):
        items = automation_service.store.list(lead_id=lead_id, limit=100)
        return {"ok": True, "lead_id": lead_id, "followups": items}

    @router.get("/leads/{lead_id}/sequences")
    def get_lead_sequences(lead_id: str):
        result = automation_service.get_lead_sequences(lead_id)
        return result

    @router.post("/leads/{lead_id}/sequences/generate")
    def generate_sequence(lead_id: str, req: GenerateSequenceRequest):
        lead = {
            "id": lead_id,
            "full_name": "",
            "email": "",
            "company": "",
        }
        result = automation_service.generate_sequence(
            lead=lead,
            campaign_key=req.campaign_key,
            sequence_key=req.sequence_key,
        )
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.get("/automation-status")
    def automation_status():
        return automation_service.get_queue_status()

    @router.post("/test-email")
    def test_email(req: TestEmailRequest):
        if automation_service.send_mode != "smtp":
            return {
                "ok": False,
                "error": f"Send mode is '{automation_service.send_mode}', not 'smtp'",
                "mode": automation_service.send_mode,
            }, 400

        if not automation_service.smtp_provider:
            return {
                "ok": False,
                "error": "SMTP provider not configured",
            }, 400

        result = automation_service.smtp_provider.send(
            to_email=req.to_email,
            subject="CID — Test de configuración SMTP",
            body="Este es un email de prueba de CID — Cine Inteligente Digital.\nSi lo recibes, la configuración SMTP es correcta.",
            from_name=automation_service.from_name,
            from_email=automation_service.from_email,
            reply_to=automation_service.reply_to,
        )

        status_code = 200 if result.success else 400
        return {
            "ok": result.success,
            "mode": "smtp",
            "to_email": req.to_email,
            "message_id": result.message_id,
            "error": result.error,
            "provider_response": result.provider_response,
        }, status_code

    @router.post("/system/test-smtp")
    def test_smtp():
        if automation_service.send_mode != "smtp":
            return {
                "ok": False,
                "error": f"Send mode is '{automation_service.send_mode}', not 'smtp'",
            }, 400

        if not automation_service.smtp_provider:
            return {
                "ok": False,
                "error": "SMTP provider not configured",
            }, 400

        result = automation_service.smtp_provider.test_connection()
        status_code = 200 if result.success else 400
        return {
            "ok": result.success,
            "mode": "smtp",
            "message_id": result.message_id,
            "error": result.error,
            "provider_response": result.provider_response,
        }, status_code

    return router
