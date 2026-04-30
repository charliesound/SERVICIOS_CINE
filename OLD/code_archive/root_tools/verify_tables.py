#!/usr/bin/env python3
"""
Verification script that uses SQLAlchemy core to verify the new tables exist and can be used.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the sys.path so we can import the modules
sys.path.append(str(Path(__file__).parent / 'src'))

from sqlalchemy import text, Table, Column, String, DateTime, Boolean, MetaData, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


async def main():
    print("=== Verifying Tables via SQLAlchemy Core ===\n")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return 1
    
    print(f"Using database: {database_url}")
    
    # Create async engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    try:
        async with async_session() as conn:
            # Start a transaction
            trans = await conn.begin()
            
            # 1. Check that the tables exist
            print("1. Checking table existence...")
            tables_to_check = ['opportunity_trackings', 'requirement_checklist_items', 'notifications']
            for table_name in tables_to_check:
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
                    {"name": table_name}
                )
                if result.fetchone():
                    print(f"   ✓ Table '{table_name}' exists")
                else:
                    print(f"   ✗ Table '{table_name}' does NOT exist")
                    return 1
            print()
            
            # 2. Insert a test opportunity tracking
            print("2. Inserting test opportunity tracking...")
            project_id = 'test-project-id'
            org_id = 'test-org-id'
            funding_call_id = 'test-funding-call-id'
            
            await conn.execute(
                text("""
                    INSERT INTO opportunity_trackings 
                    (id, project_id, organization_id, funding_call_id, status, priority, notes, created_at, updated_at)
                    VALUES 
                    (:id, :project_id, :organization_id, :funding_call_id, :status, :priority, :notes, :created_at, :updated_at)
                """),
                {
                    "id": "test-tracking-id",
                    "project_id": project_id,
                    "organization_id": org_id,
                    "funding_call_id": funding_call_id,
                    "status": "interested",
                    "priority": "medium",
                    "notes": "Test tracking from core verification",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            print("   ✓ Inserted opportunity tracking")
            
            # 3. Insert a test checklist item
            print("3. Inserting test checklist item...")
            await conn.execute(
                text("""
                    INSERT INTO requirement_checklist_items 
                    (id, tracking_id, organization_id, label, requirement_type, is_fulfilled, auto_detected, notes, created_at, updated_at)
                    VALUES 
                    (:id, :tracking_id, :organization_id, :label, :requirement_type, :is_fulfilled, :auto_detected, :notes, :created_at, :updated_at)
                """),
                {
                    "id": "test-checklist-id",
                    "tracking_id": "test-tracking-id",
                    "organization_id": org_id,
                    "label": "Test checklist item",
                    "requirement_type": "document",
                    "is_fulfilled": 0,
                    "auto_detected": 0,
                    "notes": "Test checklist item from core verification",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            print("   ✓ Inserted checklist item")
            
            # 4. Insert a test notification
            print("4. Inserting test notification...")
            await conn.execute(
                text("""
                    INSERT INTO notifications 
                    (id, organization_id, project_id, tracking_id, level, title, body, is_read, created_at, updated_at)
                    VALUES 
                    (:id, :organization_id, :project_id, :tracking_id, :level, :title, :body, :is_read, :created_at, :updated_at)
                """),
                {
                    "id": "test-notification-id",
                    "organization_id": org_id,
                    "project_id": project_id,
                    "tracking_id": "test-tracking-id",
                    "level": "warning",
                    "title": "Test Notification",
                    "body": "This is a test notification from core verification",
                    "is_read": 0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            print("   ✓ Inserted notification")
            
            # 5. Query and verify the inserted data
            print("5. Querying inserted data...")
            
            # Query tracking
            result = await conn.execute(
                text("SELECT id, status, priority, notes FROM opportunity_trackings WHERE id = :id"),
                {"id": "test-tracking-id"}
            )
            tracking = result.fetchone()
            if tracking:
                print(f"   Tracking: id={tracking[0]}, status={tracking[1]}, priority={tracking[2]}, notes={tracking[3]}")
            else:
                print("   ✗ Failed to retrieve tracking")
                return 1
            
            # Query checklist item
            result = await conn.execute(
                text("SELECT id, label, is_fulfilled FROM requirement_checklist_items WHERE id = :id"),
                {"id": "test-checklist-id"}
            )
            checklist = result.fetchone()
            if checklist:
                print(f"   Checklist: id={checklist[0]}, label={checklist[1]}, is_fulfilled={bool(checklist[2])}")
            else:
                print("   ✗ Failed to retrieve checklist item")
                return 1
            
            # Query notification
            result = await conn.execute(
                text("SELECT id, level, title, is_read FROM notifications WHERE id = :id"),
                {"id": "test-notification-id"}
            )
            notification = result.fetchone()
            if notification:
                print(f"   Notification: id={notification[0]}, level={notification[1]}, title={notification[2]}, is_read={bool(notification[3])}")
            else:
                print("   ✗ Failed to retrieve notification")
                return 1
            print()
            
            # 6. Update the tracking status
            print("6. Updating tracking status...")
            await conn.execute(
                text("""
                    UPDATE opportunity_trackings 
                    SET status = :status, notes = :notes, updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "id": "test-tracking-id",
                    "status": "gathering_docs",
                    "notes": "Updated status from core verification",
                    "updated_at": datetime.utcnow()
                }
            )
            print("   ✓ Updated tracking status")
            
            # Verify the update
            result = await conn.execute(
                text("SELECT status, notes FROM opportunity_trackings WHERE id = :id"),
                {"id": "test-tracking-id"}
            )
            updated = result.fetchone()
            if updated and updated[0] == "gathering_docs":
                print(f"   Verified update: status={updated[0]}, notes={updated[1]}")
            else:
                print("   ✗ Failed to verify tracking update")
                return 1
            print()
            
            # 7. Mark notification as read
            print("7. Marking notification as read...")
            await conn.execute(
                text("""
                    UPDATE notifications 
                    SET is_read = :is_read, updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "id": "test-notification-id",
                    "is_read": 1,
                    "updated_at": datetime.utcnow()
                }
            )
            print("   ✓ Marked notification as read")
            
            # Verify the update
            result = await conn.execute(
                text("SELECT is_read FROM notifications WHERE id = :id"),
                {"id": "test-notification-id"}
            )
            marked = result.fetchone()
            if marked and marked[0] == 1:
                print(f"   Verified mark as read: is_read={bool(marked[0])}")
            else:
                print("   ✗ Failed to verify notification mark as read")
                return 1
            print()
            
            # 8. Clean up: delete the test data (in reverse order due to foreign keys)
            print("8. Cleaning up test data...")
            await conn.execute(
                text("DELETE FROM notifications WHERE id = :id"),
                {"id": "test-notification-id"}
            )
            await conn.execute(
                text("DELETE FROM requirement_checklist_items WHERE id = :id"),
                {"id": "test-checklist-id"}
            )
            await conn.execute(
                text("DELETE FROM opportunity_trackings WHERE id = :id"),
                {"id": "test-tracking-id"}
            )
            print("   ✓ Deleted test data")
            
            # Commit the transaction
            await trans.commit()
        
        print("=== All tests passed! ===")
        print("\nThe tables for opportunity tracking, checklist, and notifications are working correctly.")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        # Rollback the transaction if it was started
        if 'trans' in locals():
            await trans.rollback()
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)