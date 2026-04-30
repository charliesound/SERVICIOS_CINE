import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the sys.path so we can import the modules
sys.path.append(str(Path(__file__).parent / 'src'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.production import (
    OpportunityTracking,
    RequirementChecklistItem,
    Notification,
    Project,
    FundingCall,
)
from src.models.core import Organization
from src.services.project_funding_service import project_funding_service

async def test_service():
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set")
        return
    
    # Convert to async SQLAlchemy URL
    if database_url.startswith("sqlite+aiosqlite://"):
        # Already async
        async_db_url = database_url
    else:
        # Assume it's synchronous and convert
        async_db_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    
    print(f"Using database URL: {async_db_url}")
    
    # Create async engine and session
    engine = create_async_engine(async_db_url, echo=False)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as db:
        # Get a project and funding call for testing
        # We'll use the first ones we find
        result = await db.execute(
            select(Project).limit(1)
        )
        project = result.scalar_one_or_none()
        if not project:
            print("No project found")
            return
        
        result = await db.execute(
            select(FundingCall).limit(1)
        )
        funding_call = result.scalar_one_or_none()
        if not funding_call:
            print("No funding call found")
            return
        
        org_id = project.organization_id
        print(f"Using project {project.id}, funding call {funding_call.id}, organization {org_id}")
        
        # Create a tracking
        tracking = await project_funding_service.create_tracking(
            db=db,
            project_id=project.id,
            organization_id=org_id,
            funding_call_id=funding_call.id,
            status="interested",
            priority="high",
            notes="Test tracking from service test"
        )
        print(f"Created tracking: {tracking}")
        tracking_id = tracking["id"]
        
        # Get the tracking
        retrieved = await project_funding_service.get_tracking(
            db=db,
            tracking_id=tracking_id,
            organization_id=org_id
        )
        print(f"Retrieved tracking: {retrieved}")
        
        # Update the tracking
        updated = await project_funding_service.update_tracking(
            db=db,
            tracking_id=tracking_id,
            organization_id=org_id,
            status="gathering_docs",
            notes="Updated notes"
        )
        print(f"Updated tracking: {updated}")
        
        # Get the checklist for the tracking
        checklist_items = await project_funding_service.get_checklist_for_tracking(
            db=db,
            tracking_id=tracking_id,
            organization_id=org_id
        )
        print(f"Checklist items ({len(checklist_items)}):")
        for item in checklist_items:
            print(f"  - {item}")
        
        # If there are checklist items, update one
        if checklist_items:
            item_id = checklist_items[0]["id"]
            updated_item = await project_funding_service.update_checklist_item(
                db=db,
                item_id=item_id,
                organization_id=org_id,
                is_fulfilled=True,
                notes="Updated via test"
            )
            print(f"Updated checklist item: {updated_item}")
        
        # Test notifications: create a notification
        await project_funding_service._create_notification(
            db=db,
            organization_id=org_id,
            project_id=project.id,
            tracking_id=tracking_id,
            level="warning",
            title="Test Notification",
            body="This is a test notification from service test"
        )
        print("Created notification")
        
        # Get notifications for the project
        notifications = await project_funding_service.get_notifications_for_project(
            db=db,
            project_id=project.id,
            organization_id=org_id
        )
        print(f"Notifications ({len(notifications)}):")
        for n in notifications:
            print(f"  - {n}")
        
        # Mark the first notification as read if any
        if notifications:
            notif_id = notifications[0]["id"]
            marked = await project_funding_service.mark_notification_as_read(
                db=db,
                notification_id=notif_id,
                organization_id=org_id
            )
            print(f"Marked notification as read: {marked}")
        
        # Clean up: delete the tracking
        deleted = await project_funding_service.delete_tracking(
            db=db,
            tracking_id=tracking_id,
            organization_id=org_id
        )
        print(f"Deleted tracking: {deleted}")
        
        # Verify the tracking is gone
        tracking_after_delete = await project_funding_service.get_tracking(
            db=db,
            tracking_id=tracking_id,
            organization_id=org_id
        )
        print(f"Tracking after delete: {tracking_after_delete}")
        
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_service())
