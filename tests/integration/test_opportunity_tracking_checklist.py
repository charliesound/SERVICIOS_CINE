from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import delete

from app import app
from database import AsyncSessionLocal
from models.core import Organization, Project
from models.production import (
    FundingCall,
    FundingSource,
    Notification,
    OpportunityTracking,
    RequirementChecklistItem,
)
from services.project_funding_service import project_funding_service


@pytest.mark.asyncio
async def test_opportunity_tracking_checklist_notifications():
    org_id = f"org-opportunity-{uuid.uuid4().hex[:12]}"
    project_id = f"project-opportunity-{uuid.uuid4().hex[:12]}"
    source_id = f"source-opportunity-{uuid.uuid4().hex[:12]}"
    funding_call_id = f"call-opportunity-{uuid.uuid4().hex[:12]}"

    with TestClient(app):
        async with AsyncSessionLocal() as db:
            organization = Organization(
                id=org_id,
                name="Opportunity Tracking Test Org",
                billing_plan="free",
                is_active=True,
            )
            project = Project(
                id=project_id,
                organization_id=org_id,
                name="Opportunity Tracking Test Project",
                description="Integration cleanup validation",
                status="development",
                script_text="INT. TEST LAB - DAY\nA producer reviews the funding pipeline.",
            )
            funding_source = FundingSource(
                id=source_id,
                organization_id=org_id,
                name="ICAA Test Source",
                code=f"ICAA-{uuid.uuid4().hex[:8]}",
                agency_name="ICAA",
                description="Synthetic source for integration validation",
                region_scope="spain",
                country_or_program="Spain",
                region="ES",
                territory="national",
                source_type="institutional",
                verification_status="official",
                is_active=True,
            )
            funding_call = FundingCall(
                id=funding_call_id,
                source_id=source_id,
                title="ICAA Development Call",
                region_scope="spain",
                country_or_program="Spain",
                agency_name="ICAA",
                region="ES",
                territory="national",
                status="open",
                verification_status="official",
            )

            db.add(organization)
            db.add(project)
            db.add(funding_source)
            await db.commit()

            db.add(funding_call)
            await db.commit()

            try:
                tracking = await project_funding_service.create_tracking(
                    db=db,
                    project_id=project.id,
                    organization_id=org_id,
                    funding_call_id=funding_call.id,
                    status="interested",
                    priority="high",
                    notes="Test tracking",
                )
                assert tracking is not None
                assert tracking["id"] is not None
                assert tracking["project_id"] == project.id
                assert tracking["organization_id"] == org_id
                assert tracking["funding_call_id"] == funding_call.id
                assert tracking["status"] == "interested"
                assert tracking["priority"] == "high"
                assert tracking["notes"] == "Test tracking"

                tracking_id = tracking["id"]

                retrieved = await project_funding_service.get_tracking(
                    db=db,
                    tracking_id=tracking_id,
                    organization_id=org_id,
                )
                assert retrieved is not None
                assert retrieved["id"] == tracking_id

                updated = await project_funding_service.update_tracking(
                    db=db,
                    tracking_id=tracking_id,
                    organization_id=org_id,
                    status="gathering_docs",
                    notes="Updated notes",
                )
                assert updated is not None
                assert updated["status"] == "gathering_docs"
                assert updated["notes"] == "Updated notes"

                checklist_items = await project_funding_service.get_checklist_for_tracking(
                    db=db,
                    tracking_id=tracking_id,
                    organization_id=org_id,
                )
                assert isinstance(checklist_items, list)

                if checklist_items:
                    item_id = checklist_items[0]["id"]
                    updated_item = await project_funding_service.update_checklist_item(
                        db=db,
                        item_id=item_id,
                        organization_id=org_id,
                        is_fulfilled=True,
                        notes="Updated via test",
                    )
                    assert updated_item is not None
                    assert updated_item["is_fulfilled"] is True
                    assert updated_item["notes"] == "Updated via test"

                await project_funding_service._create_notification(
                    db=db,
                    organization_id=org_id,
                    project_id=project.id,
                    tracking_id=tracking_id,
                    level="warning",
                    title="Test Notification",
                    body="This is a test notification",
                )

                notifications = await project_funding_service.get_notifications_for_project(
                    db=db,
                    project_id=project.id,
                    organization_id=org_id,
                )
                assert len(notifications) > 0

                test_notification = None
                for notification in notifications:
                    if notification["title"] == "Test Notification":
                        test_notification = notification
                        break

                assert test_notification is not None
                assert test_notification["body"] == "This is a test notification"
                assert test_notification["is_read"] is False

                marked = await project_funding_service.mark_notification_as_read(
                    db=db,
                    notification_id=test_notification["id"],
                    organization_id=org_id,
                )
                assert marked is not None
                assert marked["is_read"] is True

                deleted = await project_funding_service.delete_tracking(
                    db=db,
                    tracking_id=tracking_id,
                    organization_id=org_id,
                )
                assert deleted is True

                tracking_after_delete = await project_funding_service.get_tracking(
                    db=db,
                    tracking_id=tracking_id,
                    organization_id=org_id,
                )
                assert tracking_after_delete is None
            finally:
                await db.execute(delete(Notification).where(Notification.organization_id == org_id))
                await db.execute(
                    delete(RequirementChecklistItem).where(
                        RequirementChecklistItem.organization_id == org_id
                    )
                )
                await db.execute(
                    delete(OpportunityTracking).where(OpportunityTracking.organization_id == org_id)
                )
                await db.execute(delete(FundingCall).where(FundingCall.id == funding_call_id))
                await db.execute(delete(FundingSource).where(FundingSource.id == source_id))
                await db.execute(delete(Project).where(Project.id == project_id))
                await db.execute(delete(Organization).where(Organization.id == org_id))
                await db.commit()
