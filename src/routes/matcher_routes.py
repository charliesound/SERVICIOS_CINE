from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from models.matcher import MatcherJob, MatcherJobStatus
from schemas.matcher_schema import (
    MatcherJobResponse,
    MatcherJobListResponse,
    MatcherTriggerRequest,
    MatcherStatusResponse
)
from services.project_funding_service import project_funding_service

router = APIRouter(prefix="/api/projects/{project_id}/funding/matcher", tags=["matcher"])


@router.post("/trigger", response_model=MatcherJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_matcher_job(
    project_id: str = Path(..., description="Project ID"),
    organization_id: str = Query(..., description="Organization ID for tenant safety"),
    request: MatcherTriggerRequest = MatcherTriggerRequest(),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger a matcher job for a project."""
    from services.queue_service import queue_service
    from models.matcher import MatcherJob
    import hashlib
    import json
    
    # Verify project belongs to organization (tenant safety)
    from models.core import Project
    from sqlalchemy import select
    
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Compute input hash based on request parameters or current state
    # For manual trigger, we'll use current document and funding call states
    from models.document import ProjectDocument, ProjectDocumentUploadStatus, ProjectDocumentVisibilityScope
    from models.production import FundingCall, FundingSource
    
    # Get all completed PROJECT-scoped documents for this project
    docs_result = await db.execute(
        select(ProjectDocument.id, ProjectDocument.checksum)
        .where(
            ProjectDocument.project_id == project_id,
            ProjectDocument.organization_id == organization_id,
            ProjectDocument.visibility_scope == ProjectDocumentVisibilityScope.PROJECT,
            ProjectDocument.upload_status == ProjectDocumentUploadStatus.COMPLETED
        )
        .order_by(ProjectDocument.id)
    )
    document_entries = [(str(row.id), str(row.checksum)) for row in docs_result.fetchall()]
    
    # Get all funding calls for the organization (through funding_source)
    calls_result = await db.execute(
        select(FundingCall.id, FundingCall.ingested_at)
        .select_from(FundingCall)
        .join(FundingSource, FundingCall.source_id == FundingSource.id)
        .where(FundingSource.organization_id == organization_id)
        .order_by(FundingCall.id)
    )
    call_entries = [(str(row.id), row.ingested_at.isoformat() if row.ingested_at else "") 
                    for row in calls_result.fetchall()]
    
    # Matcher evaluation version
    evaluation_version = request.evaluation_version or "v1.0"
    
    # Create input hash
    hash_input = {
        "documents": document_entries,
        "funding_calls": call_entries,
        "evaluation_version": evaluation_version
    }
    
    hash_string = json.dumps(hash_input, sort_keys=True)
    input_hash = hashlib.sha256(hash_string.encode()).hexdigest()
    
    # Check if we already have a completed job with this input hash
    existing_job_result = await db.execute(
        select(MatcherJob)
        .where(
            MatcherJob.project_id == project_id,
            MatcherJob.organization_id == organization_id,
            MatcherJob.input_hash == input_hash,
            MatcherJob.status.in_([MatcherJobStatus.COMPLETED, MatcherJobStatus.SKIPPED])
        )
    )
    existing_job = existing_job_result.scalar_one_or_none()
    
    if existing_job:
        # Return existing completed job
        return MatcherJobResponse.from_orm(existing_job)
        
    # Check if there's already a pending/queued job with same hash
    pending_job_result = await db.execute(
        select(MatcherJob)
        .where(
            MatcherJob.project_id == project_id,
            MatcherJob.organization_id == organization_id,
            MatcherJob.input_hash == input_hash,
            MatcherJob.status.in_([MatcherJobStatus.PENDING, MatcherJobStatus.QUEUED, MatcherJobStatus.PROCESSING])
        )
    )
    pending_job = pending_job_result.scalar_one_or_none()
    
    if pending_job:
        # Return existing pending job
        return MatcherJobResponse.from_orm(pending_job)
    
        # Create new matcher job
        new_job = MatcherJob(
            project_id=project_id,
            organization_id=organization_id,
            trigger_type="manual",
            trigger_ref_id=None,
            input_hash=input_hash,
            status=MatcherJobStatus.QUEUED
        )
    
        db.add(new_job)
        await db.flush()
    
        # Enqueue job for processing
        queue_service.enqueue(
            job_id=str(new_job.id),
            task_type="matcher",
            backend="matcher",  # Using matcher as backend type
            priority=0,
            user_plan="free",  # Default plan
            user_id=None
        )
    
        await db.commit()
        await db.refresh(new_job)
        print(f"[DEBUG] Created matcher job with ID: {new_job.id}")
    
        return MatcherJobResponse.from_orm(new_job)


@router.get("/status", response_model=MatcherStatusResponse)
async def get_matcher_status(
    project_id: str = Path(..., description="Project ID"),
    organization_id: str = Query(..., description="Organization ID for tenant safety"),
    db: AsyncSession = Depends(get_db)
):
    """Get the latest matcher job status for a project."""
    from sqlalchemy import select
    from models.matcher import MatcherJob
    
    # Verify project belongs to organization (tenant safety)
    from models.core import Project
    
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Get latest matcher job for this project
    result = await db.execute(
        select(MatcherJob)
        .where(
            MatcherJob.project_id == project_id,
            MatcherJob.organization_id == organization_id
        )
        .order_by(MatcherJob.created_at.desc())
        .limit(1)
    )
    latest_job = result.scalar_one_or_none()
    
    if not latest_job:
        # Return default status if no jobs exist
        return MatcherStatusResponse(
            project_id=project_id,
            organization_id=organization_id,
            latest_job_id=None,
            latest_job_status=None,
            latest_job_created_at=None,
            latest_job_finished_at=None,
            total_jobs_count=0
        )
    
    # Get total jobs count
    count_result = await db.execute(
        select(MatcherJob.id)
        .where(
            MatcherJob.project_id == project_id,
            MatcherJob.organization_id == organization_id
        )
    )
    total_count = len(list(count_result.scalars().all()))
    
    return MatcherStatusResponse(
        project_id=project_id,
        organization_id=organization_id,
        latest_job_id=str(latest_job.id),
        latest_job_status=latest_job.status,
        latest_job_created_at=latest_job.created_at,
        latest_job_finished_at=latest_job.finished_at,
        total_jobs_count=total_count
    )


@router.get("/jobs", response_model=MatcherJobListResponse)
async def get_matcher_jobs(
    project_id: str = Path(..., description="Project ID"),
    organization_id: str = Query(..., description="Organization ID for tenant safety"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Get matcher job history for a project."""
    from sqlalchemy import select
    from models.matcher import MatcherJob
    
    # Verify project belongs to organization (tenant safety)
    from models.core import Project
    
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id
        )
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    # Get matcher jobs for this project with pagination
    result = await db.execute(
        select(MatcherJob)
        .where(
            MatcherJob.project_id == project_id,
            MatcherJob.organization_id == organization_id
        )
        .order_by(MatcherJob.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    jobs = list(result.scalars().all())
    
    # Get total count
    count_result = await db.execute(
        select(MatcherJob.id)
        .where(
            MatcherJob.project_id == project_id,
            MatcherJob.organization_id == organization_id
        )
    )
    total_count = len(list(count_result.scalars().all()))
    
    return MatcherJobListResponse(
        project_id=project_id,
        organization_id=organization_id,
        jobs=[MatcherJobResponse.from_orm(job) for job in jobs],
        total_count=total_count,
        limit=limit,
        offset=offset
    )


# Worker function to process matcher jobs
async def process_matcher_job(job_id: str, project_id: str, organization_id: str, db: AsyncSession) -> None:
    """Process a matcher job - this would be called by a worker."""
    from models.matcher import MatcherJob, MatcherJobStatus
    from sqlalchemy import select, update
    import traceback
    import json
    
    try:
        # Get the job
        result = await db.execute(
            select(MatcherJob).where(MatcherJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return
            
        # Mark job as processing
        await db.execute(
            update(MatcherJob)
            .where(MatcherJob.id == job_id)
            .values(
                status=MatcherJobStatus.PROCESSING,
                started_at=db.func.now()
            )
        )
        await db.commit()
        
        # Import the funding matcher service to perform the actual matching
        from services.funding_matcher_service import funding_matcher_service
        
        # Perform the matcher computation (using RAG-enhanced matching as this is the enhanced matcher)
        result_payload = await funding_matcher_service.compute_rag_matches(
            db,
            project_id=project_id,
            organization_id=organization_id
        )
        
        # Create a result summary from the payload
        result_summary = {
            "processed_documents": len(result_payload.get("project_profile", {}).get("keywords", [])),
            "processed_funding_calls": len(result_payload.get("matches", [])),
            "matches_created": len([m for m in result_payload.get("matches", []) if m.get("matcher_mode") == "rag_enriched"]),
            "matches_updated": 0,  # We're replacing matches, so technically all are "updated"
            "message": f"Matcher job processed successfully. Found {len(result_payload.get('matches', []))} funding matches.",
            "project_profile": result_payload.get("project_profile"),
            "checklist": result_payload.get("checklist")
        }
        
        # Mark job as completed
        await db.execute(
            update(MatcherJob)
            .where(MatcherJob.id == job_id)
            .values(
                status=MatcherJobStatus.COMPLETED,
                finished_at=db.func.now(),
                result_summary_json=json.dumps(result_summary)
            )
        )
        await db.commit()
        
    except Exception as e:
        # Mark job as failed on error
        await db.execute(
            update(MatcherJob)
            .where(MatcherJob.id == job_id)
            .values(
                status=MatcherJobStatus.FAILED,
                finished_at=db.func.now(),
                error_message=str(e)
            )
        )
        await db.commit()
        # Log the error (in real implementation, use proper logging)
        print(f"Matcher job {job_id} failed: {e}")
        print(traceback.format_exc())

