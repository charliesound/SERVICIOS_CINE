"""Follow-up email routes.

Endpoints:
- GET    /api/followups
- GET    /api/followups/{followup_id}
- GET    /api/leads/{lead_id}/followups
- POST   /api/followups
- PATCH  /api/followups/{followup_id}
- POST   /api/followups/{followup_id}/send
- POST   /api/followups/{followup_id}/retry
- POST   /api/followups/test-email
- POST   /api/followups/{followup_id}/test-smtp
- GET    /api/system/email-status
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from src.services.followup_send_service import FollowUpSendService


def create_followup_routes(service: FollowUpSendService) -> APIRouter:
    router = APIRouter(prefix="/api/followups", tags=["followups"])

    class CreateFollowupRequest(BaseModel):
        lead_id: str
        template_key: str = "cid_storyboard_ia_initial"
        campaign_key: str = "cid_storyboard_ia"
        recipient_email: Optional[str] = None
        subject: Optional[str] = None
        body: Optional[str] = None
        auto_send: bool = False

    class UpdateFollowupRequest(BaseModel):
        status: Optional[str] = None
        subject: Optional[str] = None
        body: Optional[str] = None
        scheduled_at: Optional[str] = None

    class TestEmailRequest(BaseModel):
        to_email: str

    @router.get("")
    def list_followups(
        lead_id: Optional[str] = Query(None),
        campaign_key: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
        limit: int = Query(50, le=200),
        offset: int = Query(0, ge=0),
    ):
        items = service.store.list(
            lead_id=lead_id,
            campaign_key=campaign_key,
            status=status,
            limit=limit,
            offset=offset,
        )
        total = service.store.count(
            lead_id=lead_id,
            campaign_key=campaign_key,
            status=status,
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
        followup = service.store.get(followup_id)
        if not followup:
            return {"ok": False, "error": "Follow-up not found"}, 404
        return {"ok": True, "followup": followup}

    @router.post("")
    def create_followup(req: CreateFollowupRequest):
        lead = {
            "id": req.lead_id,
            "full_name": "",
            "email": req.recipient_email or "",
            "company": "",
        }
        result = service.generate_and_send(
            lead=lead,
            template_key=req.template_key,
            campaign_key=req.campaign_key,
            auto_send=req.auto_send,
        )
        if not result["success"]:
            return {"ok": False, "error": result.get("error")}, 400
        return {"ok": True, "followup": result["followup"], "auto_sent": result["auto_sent"]}

    @router.patch("/{followup_id}")
    def update_followup(followup_id: str, req: UpdateFollowupRequest):
        followup = service.store.get(followup_id)
        if not followup:
            return {"ok": False, "error": "Follow-up not found"}, 404

        updates = req.model_dump(exclude_none=True)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        updated = service.store.update(followup_id, updates)
        return {"ok": True, "followup": updated}

    @router.post("/{followup_id}/send")
    def send_followup(followup_id: str):
        result = service.send_followup(followup_id)
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.post("/{followup_id}/retry")
    def retry_followup(followup_id: str):
        result = service.retry_followup(followup_id)
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.post("/test-email")
    def test_email(req: TestEmailRequest):
        result = service.send_test_email(req.to_email)
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    @router.get("/system/email-status")
    def email_status():
        return {"ok": True, **service.get_email_status()}

    @router.post("/system/test-smtp")
    def test_smtp():
        result = service.test_smtp_connection()
        status_code = 200 if result["success"] else 400
        return {"ok": result["success"], **result}, status_code

    return router
