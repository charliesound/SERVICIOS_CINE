from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
import uuid

from models.production import (
    ProjectFundingSource, 
    ProjectBudget,
    OpportunityTracking,
    RequirementChecklistItem,
    Notification,
    ProjectFundingMatch,
    FundingCall
)
from models.core import Project


class ProjectFundingService:
    SOURCE_TYPES = ["equity", "private_investor", "pre_sale", "minimum_guarantee", "in_kind", "brand_partnership", "loan", "other"]
    STATUSES = ["secured", "negotiating", "projected"]

    async def list_sources(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> list[dict]:
        result = await db.execute(
            select(ProjectFundingSource)
            .where(
                ProjectFundingSource.project_id == project_id,
                ProjectFundingSource.organization_id == organization_id,
            )
            .order_by(ProjectFundingSource.created_at.desc())
        )
        sources = result.scalars().all()
        return [
            {
                "id": s.id,
                "project_id": s.project_id,
                "organization_id": s.organization_id,
                "source_name": s.source_name,
                "source_type": s.source_type,
                "amount": s.amount,
                "currency": s.currency,
                "status": s.status,
                "notes": s.notes,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in sources
        ]

    async def create_source(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        source_name: str,
        source_type: str,
        amount: float,
        currency: str = "EUR",
        status: str = "projected",
        notes: Optional[str] = None,
    ) -> dict:
        if source_type not in self.SOURCE_TYPES:
            source_type = "other"
        if status not in self.STATUSES:
            status = "projected"

        source = ProjectFundingSource(
            id=str(uuid.uuid4()),
            project_id=project_id,
            organization_id=organization_id,
            source_name=source_name,
            source_type=source_type,
            amount=amount,
            currency=currency,
            status=status,
            notes=notes,
        )
        db.add(source)
        await db.commit()
        await db.refresh(source)

        return {
            "id": source.id,
            "project_id": source.project_id,
            "organization_id": source.organization_id,
            "source_name": source.source_name,
            "source_type": source.source_type,
            "amount": source.amount,
            "currency": source.currency,
            "status": source.status,
            "notes": source.notes,
            "created_at": source.created_at.isoformat() if source.created_at else None,
        }

    async def update_source(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        source_id: str,
        source_name: Optional[str] = None,
        source_type: Optional[str] = None,
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        result = await db.execute(
            select(ProjectFundingSource).where(
                ProjectFundingSource.id == source_id,
                ProjectFundingSource.project_id == project_id,
                ProjectFundingSource.organization_id == organization_id,
            )
        )
        source = result.scalar_one_or_none()
        if not source:
            return None

        if source_name is not None:
            source.source_name = source_name
        if source_type is not None:
            source.source_type = source_type if source_type in self.SOURCE_TYPES else "other"
        if amount is not None:
            source.amount = amount
        if currency is not None:
            source.currency = currency
        if status is not None:
            source.status = status if status in self.STATUSES else "projected"
        if notes is not None:
            source.notes = notes

        await db.commit()
        await db.refresh(source)

        return {
            "id": source.id,
            "project_id": source.project_id,
            "organization_id": source.organization_id,
            "source_name": source.source_name,
            "source_type": source.source_type,
            "amount": source.amount,
            "currency": source.currency,
            "status": source.status,
            "notes": source.notes,
            "updated_at": source.updated_at.isoformat() if source.updated_at else None,
        }

    async def delete_source(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        source_id: str,
    ) -> bool:
        result = await db.execute(
            select(ProjectFundingSource).where(
                ProjectFundingSource.id == source_id,
                ProjectFundingSource.project_id == project_id,
                ProjectFundingSource.organization_id == organization_id,
            )
        )
        source = result.scalar_one_or_none()
        if not source:
            return False

        await db.delete(source)
        await db.commit()
        return True

    async def get_summary(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> dict:
        project_result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            return {
                "total_budget": 0.0,
                "total_secured_private_funds": 0.0,
                "total_negotiating_private_funds": 0.0,
                "total_projected_private_funds": 0.0,
                "current_funding_gap": 0.0,
                "optimistic_funding_gap": 0.0,
                "currency": "EUR",
            }

        if str(project.organization_id) != str(organization_id):
            return {
                "total_budget": 0.0,
                "total_secured_private_funds": 0.0,
                "total_negotiating_private_funds": 0.0,
                "total_projected_private_funds": 0.0,
                "current_funding_gap": 0.0,
                "optimistic_funding_gap": 0.0,
                "currency": "EUR",
            }

        budget_result = await db.execute(
            select(ProjectBudget).where(
                ProjectBudget.project_id == project_id,
            )
        )
        budget = budget_result.scalar_one_or_none()
        total_budget = budget.grand_total if budget else 0.0

        sources_result = await db.execute(
            select(ProjectFundingSource).where(
                ProjectFundingSource.project_id == project_id,
                ProjectFundingSource.organization_id == organization_id,
            )
        )
        sources = sources_result.scalars().all()

        total_secured = sum(s.amount for s in sources if s.status == "secured")
        total_negotiating = sum(s.amount for s in sources if s.status == "negotiating")
        total_projected = sum(s.amount for s in sources if s.status == "projected")

        current_funding_gap = total_budget - total_secured
        optimistic_funding_gap = total_budget - (total_secured + total_negotiating + total_projected)

        currency = "EUR"

        return {
            "total_budget": total_budget,
            "total_secured_private_funds": total_secured,
            "total_negotiating_private_funds": total_negotiating,
            "total_projected_private_funds": total_projected,
            "current_funding_gap": current_funding_gap,
            "optimistic_funding_gap": optimistic_funding_gap,
            "currency": currency,
        }

    # Opportunity Tracking Methods
    async def create_tracking(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        funding_call_id: str,
        project_funding_match_id: Optional[str] = None,
        status: str = "interested",
        priority: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict:
        # Check if there's already an active tracking for this project and funding call
        # We consider active if status is not 'won', 'rejected', or 'archived'
        existing_result = await db.execute(
            select(OpportunityTracking).where(
                and_(
                    OpportunityTracking.project_id == project_id,
                    OpportunityTracking.organization_id == organization_id,
                    OpportunityTracking.funding_call_id == funding_call_id,
                    OpportunityTracking.status.notin_(["won", "rejected", "archived"]),
                )
            )
        )
        existing_tracking = existing_result.scalar_one_or_none()
        if existing_tracking:
            # Return the existing tracking instead of creating a duplicate
            return {
                "id": existing_tracking.id,
                "project_id": existing_tracking.project_id,
                "organization_id": existing_tracking.organization_id,
                "funding_call_id": existing_tracking.funding_call_id,
                "project_funding_match_id": existing_tracking.project_funding_match_id,
                "status": existing_tracking.status,
                "priority": existing_tracking.priority,
                "owner_user_id": existing_tracking.owner_user_id,
                "notes": existing_tracking.notes,
                "created_at": existing_tracking.created_at.isoformat() if existing_tracking.created_at else None,
                "updated_at": existing_tracking.updated_at.isoformat() if existing_tracking.updated_at else None,
            }

        tracking = OpportunityTracking(
            id=str(uuid.uuid4()),
            project_id=project_id,
            organization_id=organization_id,
            funding_call_id=funding_call_id,
            project_funding_match_id=project_funding_match_id,
            status=status,
            priority=priority,
            owner_user_id=owner_user_id,
            notes=notes,
        )
        db.add(tracking)
        await db.commit()
        await db.refresh(tracking)

        # Generate initial checklist items based on the match and funding call
        await self._generate_initial_checklist(db, tracking.id, organization_id)

        return {
            "id": tracking.id,
            "project_id": tracking.project_id,
            "organization_id": tracking.organization_id,
            "funding_call_id": tracking.funding_call_id,
            "project_funding_match_id": tracking.project_funding_match_id,
            "status": tracking.status,
            "priority": tracking.priority,
            "owner_user_id": tracking.owner_user_id,
            "notes": tracking.notes,
            "created_at": tracking.created_at.isoformat() if tracking.created_at else None,
            "updated_at": tracking.updated_at.isoformat() if tracking.updated_at else None,
        }

    async def get_tracking(
        self,
        db: AsyncSession,
        tracking_id: str,
        organization_id: str,
    ) -> Optional[dict]:
        result = await db.execute(
            select(OpportunityTracking).where(
                and_(
                    OpportunityTracking.id == tracking_id,
                    OpportunityTracking.organization_id == organization_id,
                )
            )
        )
        tracking = result.scalar_one_or_none()
        if not tracking:
            return None
        return {
            "id": tracking.id,
            "project_id": tracking.project_id,
            "organization_id": tracking.organization_id,
            "funding_call_id": tracking.funding_call_id,
            "project_funding_match_id": tracking.project_funding_match_id,
            "status": tracking.status,
            "priority": tracking.priority,
            "owner_user_id": tracking.owner_user_id,
            "notes": tracking.notes,
            "created_at": tracking.created_at.isoformat() if tracking.created_at else None,
            "updated_at": tracking.updated_at.isoformat() if tracking.updated_at else None,
        }

    async def get_trackings_for_project(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> list[dict]:
        result = await db.execute(
            select(OpportunityTracking).where(
                and_(
                    OpportunityTracking.project_id == project_id,
                    OpportunityTracking.organization_id == organization_id,
                )
            ).order_by(OpportunityTracking.created_at.desc())
        )
        trackings = result.scalars().all()
        return [
            {
                "id": t.id,
                "project_id": t.project_id,
                "organization_id": t.organization_id,
                "funding_call_id": t.funding_call_id,
                "project_funding_match_id": t.project_funding_match_id,
                "status": t.status,
                "priority": t.priority,
                "owner_user_id": t.owner_user_id,
                "notes": t.notes,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in trackings
        ]

    async def update_tracking(
        self,
        db: AsyncSession,
        tracking_id: str,
        organization_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        result = await db.execute(
            select(OpportunityTracking).where(
                and_(
                    OpportunityTracking.id == tracking_id,
                    OpportunityTracking.organization_id == organization_id,
                )
            )
        )
        tracking = result.scalar_one_or_none()
        if not tracking:
            return None

        if status is not None:
            tracking.status = status
        if priority is not None:
            tracking.priority = priority
        if owner_user_id is not None:
            tracking.owner_user_id = owner_user_id
        if notes is not None:
            tracking.notes = notes

        await db.commit()
        await db.refresh(tracking)

        return {
            "id": tracking.id,
            "project_id": tracking.project_id,
            "organization_id": tracking.organization_id,
            "funding_call_id": tracking.funding_call_id,
            "project_funding_match_id": tracking.project_funding_match_id,
            "status": tracking.status,
            "priority": tracking.priority,
            "owner_user_id": tracking.owner_user_id,
            "notes": tracking.notes,
            "created_at": tracking.created_at.isoformat() if tracking.created_at else None,
            "updated_at": tracking.updated_at.isoformat() if tracking.updated_at else None,
        }

    async def delete_tracking(
        self,
        db: AsyncSession,
        tracking_id: str,
        organization_id: str,
    ) -> bool:
        result = await db.execute(
            select(OpportunityTracking).where(
                and_(
                    OpportunityTracking.id == tracking_id,
                    OpportunityTracking.organization_id == organization_id,
                )
            )
        )
        tracking = result.scalar_one_or_none()
        if not tracking:
            return False

        await db.delete(tracking)
        await db.commit()
        return True

    # Checklist Methods
    async def get_checklist_for_tracking(
        self,
        db: AsyncSession,
        tracking_id: str,
        organization_id: str,
    ) -> list[dict]:
        result = await db.execute(
            select(RequirementChecklistItem).where(
                and_(
                    RequirementChecklistItem.tracking_id == tracking_id,
                    RequirementChecklistItem.organization_id == organization_id,
                )
            ).order_by(RequirementChecklistItem.created_at)
        )
        items = result.scalars().all()
        return [
            {
                "id": item.id,
                "tracking_id": item.tracking_id,
                "organization_id": item.organization_id,
                "label": item.label,
                "requirement_type": item.requirement_type,
                "is_fulfilled": item.is_fulfilled,
                "auto_detected": item.auto_detected,
                "linked_project_document_id": item.linked_project_document_id,
                "evidence_excerpt": item.evidence_excerpt,
                "due_date": item.due_date.isoformat() if item.due_date else None,
                "notes": item.notes,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in items
        ]

    async def update_checklist_item(
        self,
        db: AsyncSession,
        item_id: str,
        organization_id: str,
        label: Optional[str] = None,
        requirement_type: Optional[str] = None,
        is_fulfilled: Optional[bool] = None,
        auto_detected: Optional[bool] = None,
        linked_project_document_id: Optional[str] = None,
        evidence_excerpt: Optional[str] = None,
        due_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        result = await db.execute(
            select(RequirementChecklistItem).where(
                and_(
                    RequirementChecklistItem.id == item_id,
                    RequirementChecklistItem.organization_id == organization_id,
                )
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return None

        if label is not None:
            item.label = label
        if requirement_type is not None:
            item.requirement_type = requirement_type
        if is_fulfilled is not None:
            item.is_fulfilled = is_fulfilled
        if auto_detected is not None:
            item.auto_detected = auto_detected
        if linked_project_document_id is not None:
            item.linked_project_document_id = linked_project_document_id
        if evidence_excerpt is not None:
            item.evidence_excerpt = evidence_excerpt
        if due_date is not None:
            item.due_date = due_date
        if notes is not None:
            item.notes = notes

        await db.commit()
        await db.refresh(item)

        return {
            "id": item.id,
            "tracking_id": item.tracking_id,
            "organization_id": item.organization_id,
            "label": item.label,
            "requirement_type": item.requirement_type,
            "is_fulfilled": item.is_fulfilled,
            "auto_detected": item.auto_detected,
            "linked_project_document_id": item.linked_project_document_id,
            "evidence_excerpt": item.evidence_excerpt,
            "due_date": item.due_date.isoformat() if item.due_date else None,
            "notes": item.notes,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    # Helper methods
    async def _generate_initial_checklist(
        self,
        db: AsyncSession,
        tracking_id: str,
        organization_id: str,
    ) -> None:
        # Get the tracking to see which match and call we are dealing with
        tracking_result = await db.execute(
            select(OpportunityTracking).where(OpportunityTracking.id == tracking_id)
        )
        tracking = tracking_result.scalar_one_or_none()
        if not tracking:
            return

        # We'll generate checklist items from:
        # 1. The project_funding_match (if exists) - missing_documents, blocking_reasons, etc.
        # 2. The funding_call - requirements_json if available
        # 3. Any other relevant data

        # For now, we'll create a simple checklist based on the match's missing_documents and blocking_reasons
        # In the future, we can also parse the funding_call's requirements_json

        if tracking.project_funding_match_id:
            match_result = await db.execute(
                select(ProjectFundingMatch).where(
                    ProjectFundingMatch.id == tracking.project_funding_match_id
                )
            )
            match = match_result.scalar_one_or_none()
            if match:
                # Process missing_documents
                if match.missing_documents:
                    # Assuming missing_documents is a comma-separated string or JSON; we'll treat as plain text for now
                    docs = [d.strip() for d in match.missing_documents.split(",") if d.strip()]
                    for doc in docs:
                        checklist_item = RequirementChecklistItem(
                            id=str(uuid.uuid4()),
                            tracking_id=tracking_id,
                            organization_id=organization_id,
                            label=f"Provide document: {doc}",
                            requirement_type="document",
                            is_fulfilled=False,
                            auto_detected=False,  # We'll try to auto-detect later if possible
                            notes="Identified from funding match analysis",
                        )
                        db.add(checklist_item)

                # Process blocking_reasons
                if match.blocking_reasons:
                    # Similarly, split by comma or treat as one item
                    reasons = [r.strip() for r in match.blocking_reasons.split(",") if r.strip()]
                    for reason in reasons:
                        checklist_item = RequirementChecklistItem(
                            id=str(uuid.uuid4()),
                            tracking_id=tracking_id,
                            organization_id=organization_id,
                            label=f"Address blocking reason: {reason}",
                            requirement_type="eligibility",
                            is_fulfilled=False,
                            auto_detected=False,
                            notes="Identified from funding match analysis",
                        )
                        db.add(checklist_item)

        # TODO: Also generate from funding_call's requirements_json if available
        # For now, we commit what we have
        await db.commit()

    async def _create_notification(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str,
        tracking_id: Optional[str],
        level: str,
        title: str,
        body: Optional[str] = None,
    ) -> None:
        notification = Notification(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            project_id=project_id,
            tracking_id=tracking_id,
            level=level,
            title=title,
            body=body,
            is_read=False,
        )
        db.add(notification)
        await db.commit()

    async def check_and_create_deadline_alerts(
        self,
        db: AsyncSession,
    ) -> None:
        """
        Check for upcoming deadlines in trackings and create notifications.
        This method should be called periodically (e.g., daily).
        """
        # Get all active trackings (not won, rejected, archived) that have a project_funding_match with a deadline
        # We'll join with ProjectFundingMatch to get the deadline
        from sqlalchemy import join
        result = await db.execute(
            select(OpportunityTracking, ProjectFundingMatch)
            .select_from(
                join(
                    OpportunityTracking,
                    ProjectFundingMatch,
                    OpportunityTracking.project_funding_match_id == ProjectFundingMatch.id,
                    isouter=True,  # We still want trackings without matches? But deadline is in match.
                )
            )
            .where(
                and_(
                    OpportunityTracking.status.notin_(["won", "rejected", "archived"]),
                    ProjectFundingMatch.deadline.isnot(None),  # Only those with a deadline
                )
            )
        )
        rows = result.all()

        now = datetime.utcnow()
        for tracking, match in rows:
            if not match or not match.deadline:
                continue

            deadline = match.deadline
            days_until = (deadline - now).days

            # Check if we already have a notification for this tracking and deadline to avoid duplicates
            # We'll look for a notification with the same tracking_id and a title containing the deadline
            # For simplicity, we'll just create a new one every time and rely on the job to not run too often.
            # In a production system, we'd want to check for recent notifications.

            if days_until <= 7:
                level = "critical"
                title = f"Deadline approaching: {match.title or 'Funding Call'}"
                body = f"The deadline is in {days_until} day(s) on {deadline.strftime('%Y-%m-%d')}."
            elif days_until <= 14:
                level = "warning"
                title = f"Deadline approaching: {match.title or 'Funding Call'}"
                body = f"The deadline is in {days_until} days on {deadline.strftime('%Y-%m-%d')}."
            else:
                continue  # No alert needed

            # Create the notification
            await self._create_notification(
                db,
                organization_id=tracking.organization_id,
                project_id=tracking.project_id,
                tracking_id=tracking.id,
                level=level,
                title=title,
                body=body,
            )

        # Also, we might want to check for deadlines in the funding_call directly if there's no match?
        # But the requirement says to use the match. We'll stick to the match for now.

    # Notification Methods
    async def get_notifications_for_project(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> list[dict]:
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.project_id == project_id,
                    Notification.organization_id == organization_id,
                )
            ).order_by(Notification.created_at.desc())
        )
        notifications = result.scalars().all()
        return [
            {
                "id": n.id,
                "organization_id": n.organization_id,
                "project_id": n.project_id,
                "tracking_id": n.tracking_id,
                "level": n.level,
                "title": n.title,
                "body": n.body,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ]

    async def mark_notification_as_read(
        self,
        db: AsyncSession,
        notification_id: str,
        organization_id: str,
    ) -> Optional[dict]:
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.organization_id == organization_id,
                )
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            return None

        notification.is_read = True
        await db.commit()
        await db.refresh(notification)

        return {
            "id": notification.id,
            "organization_id": notification.organization_id,
            "project_id": notification.project_id,
            "tracking_id": notification.tracking_id,
            "level": notification.level,
            "title": notification.title,
            "body": notification.body,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
        }

project_funding_service = ProjectFundingService()
