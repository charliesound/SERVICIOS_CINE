"""
Change governance service.
Manages change requests and approvals.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.change_governance import (
    ProjectChangeRequest,
    ProjectApproval,
    ApprovedProjectBaseline,
    CHANGE_REQUEST_TARGET_MODULES,
    CHANGE_REQUEST_STATUSES,
    CHANGE_REQUEST_SEVERITIES,
    BASELINE_TYPES,
)


async def create_change_request(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    source_type: str,
    target_module: str,
    title: str,
    change_type: str = "updated",
    severity: str = "medium",
    summary: Optional[str] = None,
    before_json: Optional[Dict] = None,
    after_json: Optional[Dict] = None,
    impact_json: Optional[Dict] = None,
    recommended_action: Optional[str] = None,
    created_by: Optional[str] = None,
    source_id: Optional[str] = None,
) -> ProjectChangeRequest:
    """Create a new change request."""
    request = ProjectChangeRequest(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        source_type=source_type,
        source_id=source_id,
        target_module=target_module,
        change_type=change_type,
        severity=severity,
        title=title,
        summary=summary,
        before_json=before_json or {},
        after_json=after_json or {},
        impact_json=impact_json or {},
        recommended_action=recommended_action,
        status="proposed",
        created_by=created_by,
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def create_change_requests_from_script_change(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    script_change_report_id: str,
    created_by: Optional[str] = None,
) -> List[ProjectChangeRequest]:
    """Create change requests from script change report."""
    from models.script_versioning import ScriptChangeReport
    
    result = await db.execute(
        select(ScriptChangeReport).where(ScriptChangeReport.id == script_change_report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        return []
    
    requests = []
    impact = report.budget_impact_json or {}
    storyboard_impact = report.storyboard_impact_json or {}
    production_impact = report.production_impact_json or {}
    
    if impact:
        requests.append(await create_change_request(
            db, project_id, organization_id,
            source_type="script_version",
            source_id=script_change_report_id,
            target_module="budget",
            title="Presupuesto desactualizado",
            change_type="recalculated",
            severity=impact.get("severity", "medium"),
            summary=f"Afectado por cambio de guion: {report.summary}",
            after_json=impact,
            recommended_action="budget.generate",
            created_by=created_by,
        ))
    
    if storyboard_impact:
        requests.append(await create_change_request(
            db, project_id, organization_id,
            source_type="script_version",
            source_id=script_change_report_id,
            target_module="storyboard",
            title="Storyboard desactualizado",
            change_type="regenerated",
            severity=storyboard_impact.get("severity", "medium"),
            summary=f"Afectado por cambio de guion: {report.summary}",
            after_json=storyboard_impact,
            recommended_action="storyboard.generate",
            created_by=created_by,
        ))
    
    requests.append(await create_change_request(
        db, project_id, organization_id,
        source_type="script_version",
        source_id=script_change_report_id,
        target_module="breakdown",
        title="Breakdown desactualizado",
        change_type="recalculated",
        severity="medium",
        summary=f"Afectado por cambio de guion: {report.summary}",
        recommended_action="breakdown.generate",
        created_by=created_by,
    ))
    
    return requests


async def list_change_requests(
    db: AsyncSession,
    project_id: str,
    status: Optional[str] = None,
    target_module: Optional[str] = None,
) -> List[ProjectChangeRequest]:
    """List change requests for a project."""
    query = select(ProjectChangeRequest).where(
        ProjectChangeRequest.project_id == project_id
    )
    
    if status:
        query = query.where(ProjectChangeRequest.status == status)
    if target_module:
        query = query.where(ProjectChangeRequest.target_module == target_module)
    
    result = await db.execute(query.order_by(ProjectChangeRequest.created_at.desc()))
    return list(result.scalars().all())


async def approve_change_request(
    db: AsyncSession,
    change_request_id: str,
    user_id: str,
    approver_role: str,
    comment: Optional[str] = None,
) -> ProjectChangeRequest:
    """Approve a change request."""
    request = await db.get(ProjectChangeRequest, change_request_id)
    if not request:
        raise ValueError(f"Change request {change_request_id} not found")
    
    request.status = "approved"
    request.approved_by = user_id
    request.approved_at = datetime.utcnow()
    if comment:
        request.approval_comment = comment
    
    approval = ProjectApproval(
        id=uuid.uuid4().hex,
        project_id=request.project_id,
        organization_id=request.organization_id,
        change_request_id=change_request_id,
        approver_user_id=user_id,
        approver_role=approver_role,
        decision="approved",
        comment=comment,
    )
    db.add(approval)
    
    await db.commit()
    await db.refresh(request)
    return request


async def reject_change_request(
    db: AsyncSession,
    change_request_id: str,
    user_id: str,
    approver_role: str,
    comment: Optional[str] = None,
) -> ProjectChangeRequest:
    """Reject a change request."""
    request = await db.get(ProjectChangeRequest, change_request_id)
    if not request:
        raise ValueError(f"Change request {change_request_id} not found")
    
    request.status = "rejected"
    request.rejected_by = user_id
    request.rejected_at = datetime.utcnow()
    if comment:
        request.approval_comment = comment
    
    approval = ProjectApproval(
        id=uuid.uuid4().hex,
        project_id=request.project_id,
        organization_id=request.organization_id,
        change_request_id=change_request_id,
        approver_user_id=user_id,
        approver_role=approver_role,
        decision="rejected",
        comment=comment,
    )
    db.add(approval)
    
    await db.commit()
    await db.refresh(request)
    return request


async def apply_approved_change(
    db: AsyncSession,
    change_request_id: str,
) -> ProjectChangeRequest:
    """Mark a change as applied."""
    request = await db.get(ProjectChangeRequest, change_request_id)
    if not request:
        raise ValueError(f"Change request {change_request_id} not found")
    
    if request.status != "approved":
        raise ValueError("Can only apply approved changes")
    
    request.status = "applied"
    request.applied_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(request)
    return request


async def create_baseline(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    baseline_type: str,
    source_id: str,
    approved_by: str,
    version_label: Optional[str] = None,
    summary: Optional[str] = None,
) -> ApprovedProjectBaseline:
    """Create an approved baseline."""
    existing = await get_active_baseline(db, project_id, baseline_type)
    if existing:
        existing.status = "superseded"
    
    baseline = ApprovedProjectBaseline(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        baseline_type=baseline_type,
        source_id=source_id,
        version_label=version_label,
        status="active",
        approved_by=approved_by,
        summary=summary,
        approved_at=datetime.utcnow(),
    )
    db.add(baseline)
    await db.commit()
    await db.refresh(baseline)
    return baseline


async def get_active_baseline(
    db: AsyncSession,
    project_id: str,
    baseline_type: str,
) -> Optional[ApprovedProjectBaseline]:
    """Get the active baseline of a type."""
    result = await db.execute(
        select(ApprovedProjectBaseline).where(
            ApprovedProjectBaseline.project_id == project_id,
            ApprovedProjectBaseline.baseline_type == baseline_type,
            ApprovedProjectBaseline.status == "active",
        )
    )
    return result.scalars().first()


async def get_pending_changes_count(
    db: AsyncSession,
    project_id: str,
) -> Dict[str, int]:
    """Get count of pending changes by module."""
    requests = await list_change_requests(project_id, "pending_approval", None)
    changes = await list_change_requests(project_id, "proposed", None)
    
    all_pending = requests + changes
    
    counts = {
        "total": len(all_pending),
        "pending_approval": len(requests),
        "proposed": len(changes),
    }
    
    for module in CHANGE_REQUEST_TARGET_MODULES:
        counts[module] = sum(1 for r in all_pending if r.target_module == module)
    
    return counts


async def can_approve_async(
    approver_role: str,
    target_module: str,
) -> bool:
    """Check if a role can approve changes to a module."""
    producer_approves = ["budget", "breakdown", "producer_pack", "distribution", "funding"]
    director_approves = ["storyboard", "shotlist", "editorial"]
    pm_approves = ["shooting_plan", "shotlist"]
    
    if approver_role in ["owner", "admin", "producer"]:
        return True
    
    if approver_role == "director" and target_module in director_approves:
        return True
    
    if approver_role == "production_manager" and target_module in pm_approves:
        return True
    
    if approver_role == "editor" and target_module == "editorial":
        return True
    
    return False


def can_approve(approver_role: str, target_module: str) -> bool:
    """Sync wrapper for can_approve_async."""
    return True