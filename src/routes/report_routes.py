from datetime import date, datetime
from typing import Any, Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import User as DBUser
from models.report import CameraReport, DirectorNote, ScriptNote, SoundReport
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from schemas.report_schema import (
    CameraReportCreate,
    CameraReportListResponse,
    CameraReportResponse,
    CameraReportUpdate,
    DirectorNoteCreate,
    DirectorNoteListResponse,
    DirectorNoteResponse,
    DirectorNoteUpdate,
    ScriptNoteCreate,
    ScriptNoteListResponse,
    ScriptNoteResponse,
    ScriptNoteUpdate,
    SoundReportCreate,
    SoundReportListResponse,
    SoundReportResponse,
    SoundReportUpdate,
)
from services.report_service import report_service


router = APIRouter(prefix="/api/ingest", tags=["structured-reports"])


async def _get_user_org_id(user_id: str, db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    return user.organization_id if user else None


def _camera_report_response(report: CameraReport) -> CameraReportResponse:
    return CameraReportResponse(
        id=str(report.id),
        organization_id=str(report.organization_id),
        project_id=str(report.project_id),
        shooting_day_id=getattr(report, "shooting_day_id", None),
        sequence_id=getattr(report, "sequence_id", None),
        scene_id=getattr(report, "scene_id", None),
        shot_id=getattr(report, "shot_id", None),
        camera_label=str(report.camera_label),
        operator_name=getattr(report, "operator_name", None),
        card_or_mag=str(report.card_or_mag),
        take_reference=getattr(report, "take_reference", None),
        notes=str(report.notes),
        incidents=str(report.incidents),
        report_date=cast(date, report.report_date),
        document_asset_id=getattr(report, "document_asset_id", None),
        media_asset_id=getattr(report, "media_asset_id", None),
        created_by=getattr(report, "created_by", None),
        created_at=cast(datetime, report.created_at),
        updated_at=cast(datetime, report.updated_at),
    )


def _sound_report_response(report: SoundReport) -> SoundReportResponse:
    return SoundReportResponse(
        id=str(report.id),
        organization_id=str(report.organization_id),
        project_id=str(report.project_id),
        shooting_day_id=getattr(report, "shooting_day_id", None),
        sequence_id=getattr(report, "sequence_id", None),
        scene_id=getattr(report, "scene_id", None),
        shot_id=getattr(report, "shot_id", None),
        sound_roll=str(report.sound_roll),
        mixer_name=getattr(report, "mixer_name", None),
        boom_operator=getattr(report, "boom_operator", None),
        sample_rate=getattr(report, "sample_rate", None),
        bit_depth=getattr(report, "bit_depth", None),
        timecode_notes=getattr(report, "timecode_notes", None),
        notes=str(report.notes),
        incidents=str(report.incidents),
        report_date=cast(date, report.report_date),
        document_asset_id=getattr(report, "document_asset_id", None),
        media_asset_id=getattr(report, "media_asset_id", None),
        created_by=getattr(report, "created_by", None),
        created_at=cast(datetime, report.created_at),
        updated_at=cast(datetime, report.updated_at),
    )


def _script_note_response(report: ScriptNote) -> ScriptNoteResponse:
    return ScriptNoteResponse(
        id=str(report.id),
        organization_id=str(report.organization_id),
        project_id=str(report.project_id),
        shooting_day_id=getattr(report, "shooting_day_id", None),
        sequence_id=getattr(report, "sequence_id", None),
        scene_id=getattr(report, "scene_id", None),
        shot_id=getattr(report, "shot_id", None),
        best_take=getattr(report, "best_take", None),
        continuity_notes=str(report.continuity_notes),
        editor_note=getattr(report, "editor_note", None),
        report_date=cast(date, report.report_date),
        document_asset_id=getattr(report, "document_asset_id", None),
        media_asset_id=getattr(report, "media_asset_id", None),
        created_by=getattr(report, "created_by", None),
        created_at=cast(datetime, report.created_at),
        updated_at=cast(datetime, report.updated_at),
    )


def _director_note_response(report: DirectorNote) -> DirectorNoteResponse:
    return DirectorNoteResponse(
        id=str(report.id),
        organization_id=str(report.organization_id),
        project_id=str(report.project_id),
        shooting_day_id=getattr(report, "shooting_day_id", None),
        sequence_id=getattr(report, "sequence_id", None),
        scene_id=getattr(report, "scene_id", None),
        shot_id=getattr(report, "shot_id", None),
        preferred_take=getattr(report, "preferred_take", None),
        intention_note=str(report.intention_note),
        pacing_note=getattr(report, "pacing_note", None),
        coverage_note=getattr(report, "coverage_note", None),
        report_date=cast(date, report.report_date),
        document_asset_id=getattr(report, "document_asset_id", None),
        media_asset_id=getattr(report, "media_asset_id", None),
        created_by=getattr(report, "created_by", None),
        created_at=cast(datetime, report.created_at),
        updated_at=cast(datetime, report.updated_at),
    )


async def _get_user_org_or_401(
    current_user: Optional[UserResponse], db: AsyncSession
) -> str:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")
    return user_org_id


async def _get_report_or_404(
    db: AsyncSession, report_type: str, report_id: str, organization_id: str
) -> Any:
    report = await report_service.get_report(
        db, report_type, report_id, organization_id
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/camera-reports", response_model=CameraReportResponse)
async def create_camera_report(
    payload: CameraReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> CameraReportResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await report_service.create_report(
        db,
        "camera",
        payload.model_dump(exclude_none=True),
        user_org_id=user_org_id,
        created_by=current_user.user_id if current_user else None,
    )
    return _camera_report_response(report)


@router.get("/camera-reports", response_model=CameraReportListResponse)
async def list_camera_reports(
    project_id: Optional[str] = None,
    document_asset_id: Optional[str] = None,
    media_asset_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> CameraReportListResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    reports = await report_service.list_reports(
        db,
        "camera",
        user_org_id,
        project_id=project_id,
        document_asset_id=document_asset_id,
        media_asset_id=media_asset_id,
    )
    return CameraReportListResponse(
        reports=[_camera_report_response(report) for report in reports]
    )


@router.get("/camera-reports/{report_id}", response_model=CameraReportResponse)
async def get_camera_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> CameraReportResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "camera", report_id, user_org_id)
    return _camera_report_response(report)


@router.patch("/camera-reports/{report_id}", response_model=CameraReportResponse)
async def update_camera_report(
    report_id: str,
    payload: CameraReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> CameraReportResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "camera", report_id, user_org_id)
    updated = await report_service.update_report(
        db,
        "camera",
        report,
        payload.model_dump(exclude_none=True),
        updated_by=current_user.user_id if current_user else None,
    )
    return _camera_report_response(updated)


@router.post("/sound-reports", response_model=SoundReportResponse)
async def create_sound_report(
    payload: SoundReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> SoundReportResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await report_service.create_report(
        db,
        "sound",
        payload.model_dump(exclude_none=True),
        user_org_id=user_org_id,
        created_by=current_user.user_id if current_user else None,
    )
    return _sound_report_response(report)


@router.get("/sound-reports", response_model=SoundReportListResponse)
async def list_sound_reports(
    project_id: Optional[str] = None,
    document_asset_id: Optional[str] = None,
    media_asset_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> SoundReportListResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    reports = await report_service.list_reports(
        db,
        "sound",
        user_org_id,
        project_id=project_id,
        document_asset_id=document_asset_id,
        media_asset_id=media_asset_id,
    )
    return SoundReportListResponse(
        reports=[_sound_report_response(report) for report in reports]
    )


@router.get("/sound-reports/{report_id}", response_model=SoundReportResponse)
async def get_sound_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> SoundReportResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "sound", report_id, user_org_id)
    return _sound_report_response(report)


@router.patch("/sound-reports/{report_id}", response_model=SoundReportResponse)
async def update_sound_report(
    report_id: str,
    payload: SoundReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> SoundReportResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "sound", report_id, user_org_id)
    updated = await report_service.update_report(
        db,
        "sound",
        report,
        payload.model_dump(exclude_none=True),
        updated_by=current_user.user_id if current_user else None,
    )
    return _sound_report_response(updated)


@router.post("/script-notes", response_model=ScriptNoteResponse)
async def create_script_note(
    payload: ScriptNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> ScriptNoteResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await report_service.create_report(
        db,
        "script",
        payload.model_dump(exclude_none=True),
        user_org_id=user_org_id,
        created_by=current_user.user_id if current_user else None,
    )
    return _script_note_response(report)


@router.get("/script-notes", response_model=ScriptNoteListResponse)
async def list_script_notes(
    project_id: Optional[str] = None,
    document_asset_id: Optional[str] = None,
    media_asset_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> ScriptNoteListResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    reports = await report_service.list_reports(
        db,
        "script",
        user_org_id,
        project_id=project_id,
        document_asset_id=document_asset_id,
        media_asset_id=media_asset_id,
    )
    return ScriptNoteListResponse(
        reports=[_script_note_response(report) for report in reports]
    )


@router.get("/script-notes/{report_id}", response_model=ScriptNoteResponse)
async def get_script_note(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> ScriptNoteResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "script", report_id, user_org_id)
    return _script_note_response(report)


@router.patch("/script-notes/{report_id}", response_model=ScriptNoteResponse)
async def update_script_note(
    report_id: str,
    payload: ScriptNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> ScriptNoteResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "script", report_id, user_org_id)
    updated = await report_service.update_report(
        db,
        "script",
        report,
        payload.model_dump(exclude_none=True),
        updated_by=current_user.user_id if current_user else None,
    )
    return _script_note_response(updated)


@router.post("/director-notes", response_model=DirectorNoteResponse)
async def create_director_note(
    payload: DirectorNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DirectorNoteResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await report_service.create_report(
        db,
        "director",
        payload.model_dump(exclude_none=True),
        user_org_id=user_org_id,
        created_by=current_user.user_id if current_user else None,
    )
    return _director_note_response(report)


@router.get("/director-notes", response_model=DirectorNoteListResponse)
async def list_director_notes(
    project_id: Optional[str] = None,
    document_asset_id: Optional[str] = None,
    media_asset_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DirectorNoteListResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    reports = await report_service.list_reports(
        db,
        "director",
        user_org_id,
        project_id=project_id,
        document_asset_id=document_asset_id,
        media_asset_id=media_asset_id,
    )
    return DirectorNoteListResponse(
        reports=[_director_note_response(report) for report in reports]
    )


@router.get("/director-notes/{report_id}", response_model=DirectorNoteResponse)
async def get_director_note(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DirectorNoteResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "director", report_id, user_org_id)
    return _director_note_response(report)


@router.patch("/director-notes/{report_id}", response_model=DirectorNoteResponse)
async def update_director_note(
    report_id: str,
    payload: DirectorNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> DirectorNoteResponse:
    user_org_id = await _get_user_org_or_401(current_user, db)
    report = await _get_report_or_404(db, "director", report_id, user_org_id)
    updated = await report_service.update_report(
        db,
        "director",
        report,
        payload.model_dump(exclude_none=True),
        updated_by=current_user.user_id if current_user else None,
    )
    return _director_note_response(updated)
